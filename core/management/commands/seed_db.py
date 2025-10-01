import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

#python manage.py seed

# --- IMPORTAÇÃO DOS SEUS MODELOS (AJUSTE O 'core.models' SE NECESSÁRIO) ---
# Importe todos os modelos para os quais você precisa gerar dados
try:
    from core.models import (
        Perfil, Categoria, Produto, Pedido, PedidoVendedor, 
        ItemPedido, Cupom, Doacao, CategoriaDica, Dica, 
        CategoriaReceita, Receita, Ingrediente, EtapaPreparo, 
        Avaliacao, FaleConosco, EquipeDev
    )
    # Modelos relacionados (Ingrediente, EtapaPreparo, Avaliacao) são criados 
    # dentro da função de Receitas.
except ImportError:
    # Caso os modelos não estejam em 'core.models', altere o import acima.
    print("ERRO: Ajuste os imports no script 'seed_db.py' para o caminho correto dos seus modelos.")
    exit()

# --- CONFIGURAÇÕES DE DADOS A SEREM GERADOS ---
NUM_CLIENTES = 100
NUM_VENDEDORES = 10
NUM_ONGS = 3
NUM_PRODUTOS = 150
NUM_PEDIDOS = 50
NUM_FALE_CONOSCO = 20
NUM_MEMBROS_EQUIPE = 5
NUM_DICAS = 20
NUM_RECEITAS = 15

class Command(BaseCommand):
    help = 'Cria dados de teste (mockados) para toda a aplicação Django.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a criação de dados de teste...'))
        fake = Faker('pt_BR')
        
        # 1. LIMPEZA DE DADOS (OPCIONAL, MAS RECOMENDADO)
        self.stdout.write('Deletando dados de teste existentes...')
        
        # Limpa os dados em ordem inversa de dependência
        for Model in [
            EquipeDev, FaleConosco, Avaliacao, Ingrediente, EtapaPreparo, Receita, 
            CategoriaReceita, Dica, CategoriaDica, Doacao, ItemPedido, PedidoVendedor, 
            Pedido, Cupom, Produto, Categoria
        ]:
            Model.objects.all().delete()
            
        # Limpa Perfil e Users (exceto superusuários)
        Perfil.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Listas para armazenar objetos criados e usar em Foreign Keys
        clientes = []
        vendedores = []
        ongs = []
        produtos = []
        
        # ====================================================================
        # 2. CRIAÇÃO DE USUÁRIOS E PERFIS
        # ====================================================================

        self.stdout.write('\nCriando Usuários e Perfis (Clientes, Vendedores, ONGs)...')

        # Criar Clientes
        for i in range(NUM_CLIENTES):
            user = User.objects.create_user(
                username=fake.user_name() + str(i),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            perfil = Perfil.objects.create(
                usuario=user,
                tipo=Perfil.TipoUsuario.CLIENTE,
                telefone=fake.numerify('## #####-####'),
                endereco=fake.address()
            )
            clientes.append(perfil)
        
        # Criar Vendedores
        for i in range(NUM_VENDEDORES):
            user = User.objects.create_user(
                username='vendedor' + str(i),
                email=f'vendedor{i}@marketplace.com',
                password='password123',
            )
            perfil = Perfil.objects.create(
                usuario=user,
                tipo=Perfil.TipoUsuario.VENDEDOR,
                nome_negocio=fake.company(),
                telefone=fake.numerify('## #####-####'),
                endereco=fake.address(),
                cnpj=fake.numerify('##.###.###/####-##')
            )
            vendedores.append(perfil)

        # Criar ONGs
        for i in range(NUM_ONGS):
            user = User.objects.create_user(
                username='ong' + str(i),
                email=f'ong{i}@parceira.org',
                password='password123',
            )
            perfil = Perfil.objects.create(
                usuario=user,
                tipo=Perfil.TipoUsuario.ONG,
                nome_negocio=fake.company() + ' (ONG)',
                telefone=fake.numerify('## #####-####'),
                endereco=fake.address(),
                cnpj=fake.numerify('##.###.###/####-##'),
                descricao_parceiro=fake.paragraph(nb_sentences=5)
            )
            ongs.append(perfil)

        self.stdout.write(self.style.SUCCESS(f'Criados {len(clientes)} Clientes, {len(vendedores)} Vendedores e {len(ongs)} ONGs.'))
        
        # ====================================================================
        # 3. CRIAÇÃO DE PRODUTOS E CATEGORIAS
        # ====================================================================

        self.stdout.write('\nCriando Categorias e Produtos...')
        
        CATEGORIAS_NOMES = ['Alimentos Orgânicos', 'Roupas Sustentáveis', 'Cosméticos Naturais', 'Artesanato', 'Reciclados']
        categorias = []
        for nome in CATEGORIAS_NOMES:
            cat = Categoria.objects.create(nome=nome, slug=nome.lower().replace(' ', '-').replace('á', 'a'))
            categorias.append(cat)
            
        for i in range(NUM_PRODUTOS):
            vendedor = random.choice(vendedores)
            categoria = random.choice(categorias)
            
            # 80% dos produtos estarão ativos e com estoque
            ativo = random.choices([True, False], weights=[8, 2], k=1)[0]
            quantidade = fake.random_int(min=0, max=50) if ativo else 0
            
            # 10% dos produtos terão estoque esgotado
            if random.random() < 0.1:
                quantidade = 0
            
            produto = Produto.objects.create(
                vendedor=vendedor,
                categoria=categoria,
                nome=fake.word().capitalize() + ' ' + fake.word().capitalize(),
                descricao=fake.paragraph(nb_sentences=3),
                preco=fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=5, max_value=200),
                codigo_produto=fake.unique.bothify(text='SKU-########'),
                data_fabricacao=fake.date_this_year(),
                data_validade=fake.date_between(start_date='+1y', end_date='+3y') if random.random() < 0.3 else None,
                quantidade_estoque=quantidade,
                ativo=ativo
            )
            produtos.append(produto)
            
        self.stdout.write(self.style.SUCCESS(f'Criados {len(categorias)} Categorias e {len(produtos)} Produtos.'))

        # ====================================================================
        # 4. CRIAÇÃO DE CUPONS
        # ====================================================================
        
        self.stdout.write('\nCriando Cupons de Desconto...')
        
        CUPONS_DATA = [
            {'codigo': 'GANHE10', 'tipo': Cupom.TipoDesconto.PERCENTUAL, 'valor': 10, 'limite': 100, 'min_compra': 50},
            {'codigo': 'DESCONTO25', 'tipo': Cupom.TipoDesconto.VALOR_FIXO, 'valor': 25.00, 'limite': 50, 'min_compra': 100},
            {'codigo': 'FRETEGRATIS', 'tipo': Cupom.TipoDesconto.VALOR_FIXO, 'valor': 10.00, 'limite': 200, 'min_compra': 0},
        ]
        
        cupons = []
        for data in CUPONS_DATA:
            cupom = Cupom.objects.create(
                codigo=data['codigo'],
                tipo_desconto=data['tipo'],
                valor_desconto=data['valor'],
                data_validade=fake.date_between(start_date='+1m', end_date='+6m'),
                limite_uso=data['limite'],
                valor_minimo_compra=data['min_compra']
            )
            cupons.append(cupom)
            
        self.stdout.write(self.style.SUCCESS(f'Criados {len(cupons)} Cupons.'))

        # ====================================================================
        # 5. CRIAÇÃO DE PEDIDOS (E SUB-PEDIDOS/ITENS)
        # ====================================================================

        self.stdout.write('\nCriando Pedidos, Sub-Pedidos e Itens...')
        
        pedidos_criados = []
        for i in range(NUM_PEDIDOS):
            cliente = random.choice(clientes)
            data_pedido = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
            
            # Passo 1: Cria o Pedido Principal
            pedido_principal = Pedido.objects.create(
                cliente=cliente,
                valor_total=0.00, # Será atualizado após a criação dos sub-pedidos
                data_pedido=data_pedido,
                endereco_entrega=fake.address(),
                forma_pagamento=random.choice(Pedido.FormaPagamento.choices)[0],
                status_pagamento=random.choice(Pedido.StatusPagamento.choices)[0],
            )
            
            vendedores_selecionados = random.sample(vendedores, k=random.randint(1, min(3, len(vendedores))))
            total_pedido = 0.0
            
            # Passo 2: Cria Sub-Pedidos (um para cada vendedor)
            for vendedor in vendedores_selecionados:
                sub_pedido = PedidoVendedor.objects.create(
                    pedido_principal=pedido_principal,
                    vendedor=vendedor,
                    valor_subtotal=0.00, # Será atualizado após a criação dos itens
                    status=random.choice(PedidoVendedor.StatusPedidoVendedor.choices)[0],
                )
                
                # Passo 3: Cria Itens do Pedido para este Sub-Pedido
                # Seleciona de 1 a 5 produtos do portfólio deste vendedor
                produtos_vendedor = [p for p in produtos if p.vendedor == vendedor]
                
                if not produtos_vendedor:
                    continue 

                produtos_do_subpedido = random.sample(
                    produtos_vendedor, 
                    k=random.randint(1, min(5, len(produtos_vendedor)))
                )
                
                subtotal_vendedor = 0.0
                for produto in produtos_do_subpedido:
                    quantidade = fake.random_int(min=1, max=3)
                    preco_unitario = produto.preco
                    
                    item = ItemPedido.objects.create(
                        sub_pedido=sub_pedido,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=preco_unitario
                    )
                    subtotal_vendedor += float(item.subtotal())
                    
                # Atualiza o subtotal
                sub_pedido.valor_subtotal = subtotal_vendedor
                sub_pedido.save()
                total_pedido += subtotal_vendedor
                
            # Passo 4: Atualiza o Valor Total do Pedido Principal
            pedido_principal.valor_total = total_pedido
            pedido_principal.save()
            pedidos_criados.append(pedido_principal)

        self.stdout.write(self.style.SUCCESS(f'Criados {len(pedidos_criados)} Pedidos completos.'))

        # ====================================================================
        # 6. CRIAÇÃO DE DOAÇÕES
        # ====================================================================

        self.stdout.write('\nCriando Doações...')
        
        doacoes_criadas = []
        # Apenas vendedores podem doar
        for _ in range(NUM_VENDEDORES * 2): # 2 doações por vendedor, em média
            doador = random.choice(vendedores)
            ong = random.choice(ongs)
            data_doacao = fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            
            doacao = Doacao.objects.create(
                doador=doador,
                ong=ong,
                descricao=f'Itens diversos: {fake.word()}, {fake.word()}, {fake.word()}',
                quantidade_doada=fake.random_int(min=5, max=50),
                data_doacao=data_doacao,
                status=random.choice(Doacao.StatusDoacao.choices)[0]
            )
            doacoes_criadas.append(doacao)
            
        self.stdout.write(self.style.SUCCESS(f'Criadas {len(doacoes_criadas)} Doações.'))
        
        # ====================================================================
        # 7. CRIAÇÃO DE DICAS SUSTENTÁVEIS
        # ====================================================================

        self.stdout.write('\nCriando Dicas Sustentáveis...')
        
        CATEGORIAS_DICA = ['Reciclagem', 'Economia de Água', 'Energia Solar', 'Compostagem']
        categorias_dica = []
        for nome in CATEGORIAS_DICA:
            cat = CategoriaDica.objects.create(nome=nome, slug=nome.lower().replace(' ', '-').replace('á', 'a'))
            categorias_dica.append(cat)
            
        # Para o autor, usa-se qualquer Perfil que tenha um User (clientes, vendedores, ongs)
        autores = [p.usuario for p in clientes + vendedores + ongs]
        
        for i in range(NUM_DICAS):
            dica = Dica.objects.create(
                titulo=fake.sentence(nb_words=6),
                resumo=fake.sentence(nb_words=12),
                conteudo=fake.text(max_nb_chars=500),
                categoria=random.choice(categorias_dica),
                autor=random.choice(autores),
                publicada=True,
                data_publicacao=timezone.make_aware(fake.date_time_between(start_date='-1y', end_date='now'))
            )
            
        self.stdout.write(self.style.SUCCESS(f'Criadas {len(categorias_dica)} Categorias de Dica e {NUM_DICAS} Dicas.'))

        # ====================================================================
        # 8. CRIAÇÃO DE RECEITAS E COMPLEMENTOS
        # ====================================================================

        self.stdout.write('\nCriando Receitas, Ingredientes, Etapas e Avaliações...')
        
        CATEGORIAS_RECEITA = ['Sobremesas', 'Pratos Principais', 'Sopas', 'Aproveitamento Total']
        categorias_receita = []
        for nome in CATEGORIAS_RECEITA:
            cat = CategoriaReceita.objects.create(nome=nome, slug=nome.lower().replace(' ', '-'))
            categorias_receita.append(cat)
        
        receitas_criadas = []
        for i in range(NUM_RECEITAS):
            receita = Receita.objects.create(
                nome=fake.word().capitalize() + ' ' + random.choice(['Assado', 'Cozido', 'Grelhado', 'Salada']),
                descricao=fake.paragraph(nb_sentences=3),
                tempo_preparo=fake.random_int(min=10, max=120),
                rendimento=f'{fake.random_int(min=2, max=10)} porções',
                categoria=random.choice(categorias_receita),
                autor=random.choice(autores),
                data_criacao=fake.date_time_between(start_date='-1y', end_date='now')
            )
            receitas_criadas.append(receita)
            
            # Adiciona Ingredientes
            for j in range(random.randint(3, 7)):
                Ingrediente.objects.create(
                    receita=receita,
                    nome=fake.word(),
                    quantidade=f'{random.randint(1, 4)} {random.choice(["xícaras", "colheres", "gramas", "a gosto"])}'
                )
                
            # Adiciona Etapas de Preparo
            for j in range(random.randint(4, 8)):
                EtapaPreparo.objects.create(
                    receita=receita,
                    ordem=j + 1,
                    descricao=fake.sentence(nb_words=15)
                )

            # Adiciona Avaliações
            avaliadores = random.sample(autores, k=random.randint(3, 10))
            for avaliador in avaliadores:
                Avaliacao.objects.create(
                    receita=receita,
                    autor=avaliador,
                    nota=fake.random_int(min=1, max=5),
                    texto=fake.text(max_nb_chars=100) if random.random() < 0.7 else ''
                )

        self.stdout.write(self.style.SUCCESS(f'Criadas {len(categorias_receita)} Categorias de Receita e {len(receitas_criadas)} Receitas com detalhes e avaliações.'))

        # ====================================================================
        # 9. CRIAÇÃO DE FALE CONOSCO
        # ====================================================================

        self.stdout.write('\nCriando Mensagens de Fale Conosco...')
        
        for i in range(NUM_FALE_CONOSCO):
            FaleConosco.objects.create(
                nome=fake.name(),
                email=fake.email(),
                mensagem=fake.text(max_nb_chars=300),
                data_envio=timezone.make_aware(fake.date_time_between(start_date='-1y', end_date='now')),
                status=random.choice(FaleConosco.statusMensagem.choices)[0]
            )
            
        self.stdout.write(self.style.SUCCESS(f'Criadas {NUM_FALE_CONOSCO} Mensagens de Fale Conosco.'))

        # ====================================================================
        # 10. CRIAÇÃO DE MEMBROS DA EQUIPE
        # ====================================================================

        self.stdout.write('\nCriando Membros da Equipe de Desenvolvimento...')
        
        for i in range(NUM_MEMBROS_EQUIPE):
            EquipeDev.objects.create(
                nome=fake.name(),
                link_git=fake.url()
                # O campo 'foto' e 'logo_ong' exigem o upload de um arquivo, 
                # o que é mais complexo em um script de seed. 
                # Eles são omitidos, mas podem ser preenchidos manualmente ou com 
                # a função SimpleUploadedFile se necessário.
            )
            
        self.stdout.write(self.style.SUCCESS(f'Criados {NUM_MEMBROS_EQUIPE} Membros da Equipe Dev.'))
        
        self.stdout.write(self.style.SUCCESS('\nSEMEADURA DO BANCO DE DADOS CONCLUÍDA COM SUCESSO!'))