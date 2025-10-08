# Viewsets dos modelos principais
from .usuarioViewSet import *
from .perfilViewSet import *
from .categoriaViewset import *
from .produtoViewset import *
from .pedidoViewset import *
from .itemPedidoViewSet import *
from .receitaViewset import *

# Viewsets de conteúdo e outros
from .avaliacaoViewset import *
from .cupomViewset import *
from .dicas_sustentaveisViewset import *
from .doacaoViewsets import *
from .faleconoscoViewset import *
from .notificacaoViewset import *

# Os viewsets abaixo foram desativados por dependerem de modelos que não existem:
# from .vendedorViewset import *
# from .cadastro_produtoViewset import *
# from .comentariosViewSet import *