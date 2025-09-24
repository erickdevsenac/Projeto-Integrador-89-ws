# from rest_framework import permissions, viewsets

# from core.models import Categoria, Produto
# from core.serializers import (
#     ProdutoSerializer,
#     CategoriaSerializer,
# )
# class CategoriaViewSet(viewsets.ModelViewSet):
#     """
#     Endpoint da API para visualizar e editar categorias de produtos.
#     """
#     queryset = Categoria.objects.all()
#     serializer_class = CategoriaSerializer
#     permission_classes = [permissions.IsAdminUser] 
#     lookup_field = 'slug' 


# class ProdutoViewSet(viewsets.ModelViewSet):
#     """
#     Endpoint da API para produtos.
#     """
#     queryset = Produto.objects.all().filter(ativo=True) 
#     serializer_class = ProdutoSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#     def get_queryset(self):
#         """
#         Opcional: Filtra produtos por categoria se um parâmetro 'categoria' for passado na URL.
#         Ex: /api/produtos/?categoria=eletronicos
#         """
#         queryset = super().get_queryset()
#         categoria_slug = self.request.query_params.get('categoria')
#         if categoria_slug:
#             queryset = queryset.filter(categoria__slug=categoria_slug)
#         return queryset

#     def perform_create(self, serializer):
#         """ Sobrescrevemos o método de criação para passar o 'request' ao serializer """
#         serializer.save()


