import random
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

# from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

# --- IMPORTAÇÃO DOS SEUS MODELOS ---
try:
    from core.models import (
        Avaliacao,
        CategoriaDica,
        CategoriaProduto,
        CategoriaReceita,
        Cupom,
        Dica,
        Doacao,
        EquipeDev,
        EtapaPreparo,
        FaleConosco,
        Ingrediente,
        ItemPedido,
        PacoteSurpresa,
        Pedido,
        PedidoVendedor,
        Perfil,
        Produto,
        Receita,
    )
except ImportError as e:
    print(
        f"ERRO: Não foi possível importar os modelos. Verifique o arquivo 'core/models/__init__.py'. Detalhe: {e}"
    )
    exit()

# --- CONFIGURAÇÕES DE DADOS A SEREM GERADOS ---
NUM_CLIENTES = 50
NUM_VENDEDORES = 10
NUM_ONGS = 3
NUM_PRODUTOS = 150
NUM_PACOTES_SURPRESA = 25  # Número de pacotes a serem criados
NUM_PEDIDOS = 40
NUM_FALE_CONOSCO = 15
NUM_MEMBRO_EQUIPE = 5
NUM_DICAS = 15
NUM_RECEITAS = 10


class Command(BaseCommand):
    help = "Cria dados de teste (mockados) para toda a aplicação Django de forma eficiente."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Iniciando a semeadura do banco de dados...")
        )
        fake = Faker("pt_BR")

        # 1. LIMPEZA DE DADOS
        self.stdout.write("Deletando dados de teste existentes...")
        models_to_delete = [
            EquipeDev,
            FaleConosco,
            Avaliacao,
            Ingrediente,
            EtapaPreparo,
            Receita,
            CategoriaReceita,
            Dica,
            CategoriaDica,
            Doacao,
            ItemPedido,
            PedidoVendedor,
            Pedido,
            Cupom,
            PacoteSurpresa,
            Produto,
            CategoriaProduto,
        ]
        for Model in models_to_delete:
            Model.objects.all().delete()

        Perfil.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Dados antigos deletados."))

        # ====================================================================
        # 2. CRIAÇÃO DE USUÁRIOS E PERFIS
        # ====================================================================
        self.stdout.write("\nCriando Usuários e Perfis...")
        # (Seu código de criação de usuários e perfis permanece o mesmo)
        users_to_create = []
        for _ in range(NUM_CLIENTES):
            users_to_create.append(
                User(
                    username=fake.unique.user_name(),
                    email=fake.unique.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )
            )
        User.objects.bulk_create(users_to_create, ignore_conflicts=True)
        for user in User.objects.filter(is_superuser=False, perfil__isnull=True):
            user.set_password("password123")
            user.save()

        profiles_to_create = []
        for user in User.objects.filter(is_superuser=False, perfil__isnull=True):
            profiles_to_create.append(
                Perfil(
                    usuario=user,
                    tipo=Perfil.TipoUsuario.CLIENTE,
                    nome_completo=f"{user.first_name} {user.last_name}",
                    telefone=fake.numerify("(##) #####-####"),
                    endereco=fake.address(),
                )
            )
        Perfil.objects.bulk_create(profiles_to_create)

        for i in range(NUM_VENDEDORES):
            user = User.objects.create_user(
                f"vendedor{i}", f"vendedor{i}@marketplace.com", "password123"
            )
            Perfil.objects.create(
                usuario=user,
                tipo=Perfil.TipoUsuario.VENDEDOR,
                nome_negocio=fake.company(),
                telefone=fake.numerify("(##) #####-####"),
                endereco=fake.address(),
                cnpj=fake.cnpj(),
            )

        for i in range(NUM_ONGS):
            user = User.objects.create_user(
                f"ong{i}", f"ong{i}@parceira.org", "password123"
            )
            Perfil.objects.create(
                usuario=user,
                tipo=Perfil.TipoUsuario.ONG,
                nome_negocio=f"{fake.company()} (ONG)",
                telefone=fake.numerify("(##) #####-####"),
                endereco=fake.address(),
                cnpj=fake.cnpj(),
                descricao_parceiro=fake.paragraph(nb_sentences=5),
            )

        clientes = list(Perfil.objects.filter(tipo=Perfil.TipoUsuario.CLIENTE))
        vendedores = list(Perfil.objects.filter(tipo=Perfil.TipoUsuario.VENDEDOR))
        ongs = list(Perfil.objects.filter(tipo=Perfil.TipoUsuario.ONG))
        self.stdout.write(
            self.style.SUCCESS(
                f"Criados {len(clientes)} Clientes, {len(vendedores)} Vendedores e {len(ongs)} ONGs."
            )
        )

        # ====================================================================
        # 3. CRIAÇÃO DE CATEGORIAS E PRODUTOS
        # ====================================================================
        self.stdout.write("\nCriando Categorias e Produtos...")
        # (Seu código de criação de produtos permanece o mesmo)
        CATEGORIAS_NOMES = [
            "Alimentos Orgânicos",
            "Roupas Sustentáveis",
            "Cosméticos Naturais",
            "Artesanato",
            "Reciclados",
        ]
        categorias_prod = [
            CategoriaProduto(nome=nome, slug=slugify(nome)) for nome in CATEGORIAS_NOMES
        ]
        CategoriaProduto.objects.bulk_create(categorias_prod)
        categorias_prod = list(CategoriaProduto.objects.all())

        produtos_to_create = []
        for _ in range(NUM_PRODUTOS):
            preco = fake.pydecimal(
                left_digits=3,
                right_digits=2,
                positive=True,
                min_value=10,
                max_value=200,
            )
            preco_original = None
            motivo_desconto = None
            if random.random() < 0.2:
                preco_original = preco
                preco = round(preco * Decimal(random.uniform(0.6, 0.9)), 2)
                motivo_desconto = random.choice(Produto.MotivoDesconto.choices)[0]

            produtos_to_create.append(
                Produto(
                    vendedor=random.choice(vendedores),
                    categoria=random.choice(categorias_prod),
                    nome=f"{fake.word().capitalize()} {fake.word()}",
                    descricao=fake.paragraph(nb_sentences=3),
                    preco=preco,
                    preco_original=preco_original,
                    motivo_desconto=motivo_desconto,
                    codigo_produto=f"SKU-{uuid.uuid4().hex[:8].upper()}",
                    data_validade=(
                        fake.future_date(end_date="+2y")
                        if random.random() < 0.3
                        else None
                    ),
                    quantidade_estoque=random.randint(0, 50),
                    ativo=random.choices([True, False], weights=[0.9, 0.1])[0],
                )
            )
        Produto.objects.bulk_create(produtos_to_create)
        produtos = list(Produto.objects.filter(ativo=True, quantidade_estoque__gt=0))
        self.stdout.write(
            self.style.SUCCESS(
                f"Criadas {len(categorias_prod)} Categorias e {len(produtos_to_create)} Produtos."
            )
        )

        # ====================================================================
        # 3.5. CRIAÇÃO DE PACOTES SURPRESA (GAMIFICATION)
        # ====================================================================
        self.stdout.write("\nCriando Pacotes Surpresa...")
        if not produtos or not vendedores:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum produto ou vendedor disponível para criar pacotes. Pulando etapa."
                )
            )
        else:
            pacotes_to_create = []
            tiers = {
                "Bronze": {"preco_min": 15, "preco_max": 25, "valor_mult": 1.4},
                "Prata": {"preco_min": 30, "preco_max": 45, "valor_mult": 1.5},
                "Ouro": {"preco_min": 50, "preco_max": 70, "valor_mult": 1.6},
            }

            for _ in range(NUM_PACOTES_SURPRESA):
                tier_nome, tier_info = random.choice(list(tiers.items()))
                vendedor_selecionado = random.choice(vendedores)

                preco_pacote = fake.pydecimal(
                    left_digits=2,
                    right_digits=2,
                    positive=True,
                    min_value=tier_info["preco_min"],
                    max_value=tier_info["preco_max"],
                )
                valor_estimado_pacote = round(
                    preco_pacote
                    * Decimal(
                        random.uniform(
                            tier_info["valor_mult"], tier_info["valor_mult"] + 0.2
                        )
                    ),
                    2,
                )

                pacotes_to_create.append(
                    PacoteSurpresa(
                        vendedor=vendedor_selecionado,
                        nome=f"Pacote Surpresa {tier_nome}",
                        descricao="Uma seleção incrível de produtos da nossa loja. Pague menos e ajude a combater o desperdício!",
                        preco=preco_pacote,
                        quantidade_estoque=random.randint(3, 15),
                        ativo=True,
                        tipo_conteudo=random.choice(
                            ["Padaria", "Hortifruti", "Mercearia", "Laticínios"]
                        ),
                        instrucoes_especiais=f"Consumir preferencialmente em {random.randint(2, 5)} dias.",
                    )
                )

            PacoteSurpresa.objects.bulk_create(pacotes_to_create)
            pacotes_criados = list(PacoteSurpresa.objects.all())

            for pacote in pacotes_criados:
                num_produtos_possiveis = random.randint(2, 5)
                produtos_selecionados = random.sample(
                    produtos, k=min(num_produtos_possiveis, len(produtos))
                )
                pacote.produtos_possiveis.set(produtos_selecionados)

            self.stdout.write(
                self.style.SUCCESS(f"Criados {len(pacotes_criados)} Pacotes Surpresa.")
            )

        # ====================================================================
        # 4. CRIAÇÃO DE PEDIDOS (E SUB-PEDIDOS/ITENS)
        # ====================================================================
        self.stdout.write("\nCriando Pedidos...")
        if not produtos:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum produto disponível para criar pedidos. Pulando etapa."
                )
            )
        else:
            for _ in range(NUM_PEDIDOS):
                cliente = random.choice(clientes)
                pedido_principal = Pedido.objects.create(
                    cliente=cliente,
                    valor_total=Decimal("0.00"),
                    endereco_entrega=cliente.endereco,
                    forma_pagamento=random.choice(Pedido.FormaPagamento.choices)[0],
                    status_pagamento=random.choice(Pedido.StatusPagamento.choices)[0],
                )

                vendedores_do_pedido = {
                    p.vendedor
                    for p in random.sample(
                        produtos, k=random.randint(1, min(4, len(produtos)))
                    )
                }
                total_pedido = Decimal("0.00")

                for vendedor in vendedores_do_pedido:
                    produtos_do_vendedor_no_pedido = [
                        p
                        for p in produtos
                        if p.vendedor == vendedor
                        and p in random.sample(produtos, k=random.randint(1, 3))
                    ]
                    if not produtos_do_vendedor_no_pedido:
                        continue

                    subtotal_vendedor = sum(
                        p.preco * random.randint(1, 2)
                        for p in produtos_do_vendedor_no_pedido
                    )
                    sub_pedido = PedidoVendedor.objects.create(
                        pedido_principal=pedido_principal,
                        vendedor=vendedor,
                        valor_subtotal=subtotal_vendedor,
                        status=random.choice(
                            PedidoVendedor.StatusPedidoVendedor.choices
                        )[0],
                    )

                    itens_to_create = []
                    for produto in produtos_do_vendedor_no_pedido:
                        quantidade = random.randint(1, 2)
                        itens_to_create.append(
                            ItemPedido(
                                sub_pedido=sub_pedido,
                                produto=produto,
                                quantidade=quantidade,
                                preco_unitario=produto.preco,
                            )
                        )
                    ItemPedido.objects.bulk_create(itens_to_create)
                    total_pedido += subtotal_vendedor

                pedido_principal.valor_total = total_pedido
                pedido_principal.save()
            self.stdout.write(
                self.style.SUCCESS(f"Criados {NUM_PEDIDOS} Pedidos completos.")
            )

        self.stdout.write(
            self.style.SUCCESS("\nSEMEADURA DO BANCO DE DADOS CONCLUÍDA!")
        )
