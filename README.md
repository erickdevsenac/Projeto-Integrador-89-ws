# APROVEITE+ WEB SITE .
# 🍹 Aproveite+ com Front-End e Back-End com Django-Rest-Framework

Bem-vindo(a) ao repositório do projeto **Aproveite+**, uma aplicação web desenvolvida com **Django-Rest-Framework**!

---

## ✨ Visão Geral do Projeto

O **Aproveite+** é um aplicação web que tem como objetivo **[Conecta vendedores e produtores com potenciais clientes e tambem com diversas ong colaborando com desenvolvimento sustentável]**, o projeto visa oferecer uma experiência moderna e eficiente.

---

## 🚀 Como Iniciar

Siga os passos abaixo para configurar e rodar o projeto na sua máquina local.

### Pré-requisitos

Certifique-se de ter o seguinte instalado:

* **Django** e **Djando-Rest-Framework**.
* **Git**.

### 1. Clonando o Repositório

1.  Crie uma pasta local e abra o terminal nela.
2.  Clone o projeto usando o link do GitHub:

    ```bash
    git clone https://github.com/erickdevsenac/Projeto-Integrador-89-ws.git
    ```

3.  Entre na pasta do projeto:

    ```bash
    cd Projeto-Integrador-89-ws
    ```

### 2. Rodando a Aplicação Web Localmente

1.  **Instale as dependências** do projeto:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Inicie a aplicação**:

    ⚠️ **Verifique:** Antes de rodar, garanta que sua aplicação estaja com o ambiente virtual criado e ativado, no caso se não estiver rode o codigo
    **python -m venv nome_do_venv** e para ativar o ambiente virtual rode esse outro codigo **nome_do_venv\Scripts\activate**.

    ```bash
    py manage.py runserver
    ```

    Após a execução, o terminal exibirá um código onde tera o link para rodar sua aplicação:
    * Starting development server at http://127.0.0.1:8000/

---

## 🛠️ Estrutura do Código

A maior parte do código alterável está concentrada nas pastas **`core`**, **`projeto`** e **`templates`**:

* **`core/templates`**: Contém todas as telas da aplicação.
---

## 🤝 Contribuindo

Ficamos felizes com sua contribuição! Siga o fluxo de trabalho padrão para garantir a organização do projeto:

1.  **Crie uma nova branch** para o seu trabalho.
2.  **Fique atento(a) às Issues** criadas no Projeto (Github Projects). Vincular seus commits a uma Issue ajuda no rastreamento e organização.

## 📥 Sincronizando o repositório local

Estando com o projeto instalado e rodando na máquina local, antes de começar a desenvolver faça a sincronização da última versão do código executando os seguintes comandos:

1. **Estando na branch principal (main)** execute o comando:
   ```bash
   git pull
   ```
2. **Estando em uma branch particular** execute o comando:
   ```bash
   git pull origin main
   ```

### Fluxo de Commit

Após realizar as alterações na sua branch:

1.  **Adicione ao Stage** (preparação):

    ```bash
    git add . # Para todos os arquivos
    # ou
    git add nome-do-arquivo.js # Para arquivos específicos
    ```

2.  **Faça o Commit** com uma mensagem clara. **Sempre que possível, vincule a Issue:**

    ```bash
    # Se houver uma Issue associada:
    git commit -m "Resolves: #00 - Mensagem específica sobre a alteração"

    # Se não houver:
    git commit -m "Mensagem da alteração"
    ```

3.  **Envie as alterações** para o repositório remoto (GitHub):

    ```bash
    git push origin minha-nova-feature
    # ou, se estiver na branch correta:
    git push
    ```

---

## 📚 Aprenda Mais

Para aprofundar seus conhecimentos sobre o desenvolvimento com Djando-Rest-Framework e a estrutura do projeto:

* **[Documentação Oficial do Django](https://docs.djangoproject.com/)**: O ponto de partida fundamental.
* **[Guia do Django](https://docs.djangoproject.com/en/5.2/topics/)**: Para tópicos mais avançados.
* **[Tutorial do Django](https://docs.djangoproject.com/en/5.2/intro/)**: Um ótimo passo a passo para iniciantes.

---

Se tiver qualquer dúvida ou problema, sinta-se à vontade para abrir uma **Issue**!

