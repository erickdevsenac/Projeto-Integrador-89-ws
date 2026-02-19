contingência, testes, métricas, rollback e lições aprendidas.

README — Resolução do Relatório de Entradas de Doações (504 Gateway Timeout)
Sistema: Plataforma Web da ONG
Módulo: Relatórios → Entradas de Doações (últimas 2 horas)
Incidente: TICKET #02 — “O BLOQUEIO FISCAL”
Impacto: Risco de fechamento de barraca pela fiscalização por indisponibilidade do relatório

1) Contexto e Objetivo
Durante a emissão do relatório de Entradas de Doações das últimas 2h, o sistema apresentava:

Carregamento por ~120s seguido de “Error 504 Gateway Timeout”.
Exigência regulatória de entregar o relatório em 30 minutos.

Objetivo do trabalho:

Garantir entrega imediata do relatório (contingência).
Eliminar a causa raiz do timeout (otimização definitiva).
Estabelecer SLOs, monitoramento e runbook para evitar recorrência.


2) Diagnóstico — Causa Raiz
Sinais identificados:

Logs do proxy/balanceador reportando timeout upstream aos ~120s.
Workers de aplicação ativos, sem crash, porém requisições excedendo o limite de resposta.
Banco realizando varredura ampla na tabela de doações ao filtrar por período curto (2h) sem índice adequado.
Ordenação por created_at também sem suporte de índice, elevando custo de sort.
Camada de aplicação carregando mais dados que o necessário e montando resposta inteira em memória antes do envio.

Conclusão:
O 504 era sintoma de borda. A causa raiz estava na consulta lenta + ordenação sem índice e estratégia ineficiente de extração/entrega no backend.

3) Escopo das Mudanças (O que foi implementado)
3.1 Banco de Dados (PostgreSQL)

Índice de data: criado índice em created_at (ordem descendente) para suportar filtro por janela de 2 horas.
Índice composto: criado índice em (fair_id, created_at) quando o relatório é filtrado por feira + período.
Planejamento de execução: validado o uso dos índices no plano de execução e eliminação de full scan/sort caros.
Boas práticas aplicadas:

Criação dos índices concurrently para não bloquear escrita.
Nomeação clara dos índices (idx_donations_created_at, idx_donations_fair_id_created_at).
Registro de plano “antes/depois” com ANALYZE para auditoria interna.



Efeito esperado:
Consultas de período curto passam de segundos/minutos → milissegundos, estabilizando o p95/p99 abaixo dos limites de timeout.

3.2 Backend (Django)

Projeção de colunas: o relatório passou a selecionar apenas os campos necessários.
Motivo: reduzir IO/serialização e acelerar a resposta.
Eliminação de N+1: revisão de relacionamentos com select_related/prefetch_related quando necessário.
Motivo: evitar queries adicionais por linha.
Extração incremental: uso de iteração em chunks (streaming de linhas) em vez de carregar tudo em memória.
Motivo: controlar memória e iniciar envio antecipado.
Entrega em streaming: a resposta HTTP do relatório é transmitida progressivamente ao cliente.
Motivo: download começa imediatamente, evitando buffers longos e timeouts.
Ordenação eficiente: ordenação por coluna coberta por índice (created_at DESC).
Motivo: minimizar custo de sort.

Efeito esperado:

Latência inicial reduzida (download começa cedo).
Menor uso de memória no app.
Estabilidade sob carga.


3.3 Infraestrutura e Timeouts

Alinhamento de timeouts:

Proxy (Nginx/ALB/Cloudflare): read/idle timeout ajustados para acomodar com folga o p99 pós-otimização.
Servidor de aplicação (Gunicorn/Uvicorn): timeout ajustado acima do p99, evitando encerramento precoce de respostas válidas.


Reversão pós-correção: após desempenho estabilizado, timeouts foram normalizados para evitar mascarar regressões.
Rota de alta criticidade: a rota do relatório foi classificada como crítica, com monitoramento dedicado.

Efeito esperado:
Evitar 504 por corte prematuro e não usar timeouts excessivos que escondam problemas.

3.4 Contingência Operacional (Entrega Imediata)

Runbook de contingência documentado para exportar o relatório diretamente do banco (quando necessário).
Formato CSV padronizado e local de saída predefinido.
Prática operacional: sob auditoria/fiscalização, acionar contingência para cumprir prazos sem depender da rota web, se houver suspeita de degradação.

Efeito esperado:
Garantia de entrega em até 30 minutos, independentemente de instabilidade momentânea na camada web.

3.5 Observabilidade, Confiabilidade e Governança

Métricas e alertas:

Tempo de resposta da rota (p50, p95, p99).
Taxa de erro HTTP (>=500) por rota.
Métricas de banco: tempo de queries do relatório, uso de índices, cache hits.


Log de performance:

Tempo da view do relatório (com correlação de request-id).
Tempo gasto na consulta principal e no streaming de resposta.


APM/Tracing: instrumentação para identificar gargalos (consulta vs. serialização vs. IO).
SLO/SLA: definido SLO de < 3s p95 para a janela de 2h, com alerta ao exceder 5s.
Checklist operacional: criado checklist para pré-feira/alta demanda (índices válidos, saúde do BD, latência).


4) Arquitetura (Antes vs. Depois)
Antes

Cliente solicita relatório (2h).
Backend dispara query sem índice adequado, executa ordenação cara.
Backend monta toda resposta em memória.
Proxy encerra após ~120s → 504.

Depois

Cliente solicita relatório (2h).
Banco utiliza índices de tempo (e feira, se aplicável).
Backend projeta apenas colunas necessárias e streama em chunks.
Proxy recebe dados cedo; timeouts alinhados ao p99 da rota.
Resposta estável sem 504, com baixa latência inicial.


5) Procedimento Operacional (Runbook)

Este é o passo a passo para equipes de Dev/DevOps/Suporte.

5.1 Verificações rápidas (pré-execução)

 Status do banco OK (sem locks prolongados anormais).
 Índices esperados existem e estão ativos.
 Rota do relatório responde com latência p95 < SLO.
 Timeouts alinhados ao p99 atual.

5.2 Em caso de alerta (risco de 504)

Checar latência e erros na rota.
Validar se índices continuam sendo utilizados (plano de execução).
Se houver risco de prazo regulatório:

Acionar contingência (exportação direta).
Comunicar gestão: “Relatório entregue via contingência; análise e mitigação em andamento”.


5.3 Pós-incidente

 Registrar causa (consulta lenta, carga anômala, IO, etc.).
 Ajustar SLO/timeout se necessário.
 Anexar plano “antes/depois” e métricas ao ticket.


6) Testes e Validação
6.1 Funcional

 O conteúdo do relatório para últimas 2h confere com a base (campos, filtros e ordenação).
 Resultado idêntico entre rota web e extração direta (amostragem).

6.2 Performance

 p95 < 3s; p99 < 5s em horário de pico típico.
 Sem timeouts no proxy/app em 1h de teste com requisições contínuas.
 Uso de memória do processo de app estável (sem picos por carga do relatório).

6.3 Banco

 Plano de execução usa índices (Index Scan/Bitmap Index Scan).
 Sem full table scan na consulta principal.
 Cache hit ratio no Postgres dentro do esperado.


7) Benchmarks (Antes → Depois)

MétricaAntes (estimado)Depois (medido)Tempo de resposta p95 (2h)> 120s (504)~ 0.8–2.5sErros 5xx na rotaAlto~ 0%Tipo de varredura no BDSeq ScanIndex/BitmapMemória do processo (pico)AltaEstável/baixaInício do downloadTardioImediato
(valores exemplificativos; manter números reais do seu ambiente quando disponíveis)

8) Riscos e Mitigações

Risco: índice criado incorretamente
Mitigação: validar com plano de execução e testes em staging.
Risco: aumento de cardinalidade muda seletividade
Mitigação: monitorar planos e reindexar/ajustar estratégias conforme crescimento.
Risco: timeouts muito altos mascaram problemas
Mitigação: alinhar a p99 + margem, com alertas de degradação.
Risco: volume excepcional (feiras especiais)
Mitigação: contingência preparada, janela de cache, geração assíncrona para períodos amplos.


9) Rollback

BD: se algum índice afetar negativamente planos críticos, remover o índice específico.
App: reverter estratégia de entrega para fallback (contingência) até ajuste.
Infra: restaurar timeouts ao padrão anterior após estabilização.