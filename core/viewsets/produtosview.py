# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.exceptions import NotFound
# from core.models import Produto
# from core.serializers import ProdutoSerializer


# class ProdutoViewSet(viewsets.ModelViewSet):
#     queryset = Produto.objects.all()
#     serializer_class = ProdutoSerializer

#     def get_object(self):
#         try:
#             return super().get_object()
#         except Produto.DoesNotExist:
#             raise NotFound('Produto não encontrado.')

#     def create(self, request, *args, **kwargs):
#         try:
#             return super().create(request, *args, **kwargs)
#         except Exception as e:
#             return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, *args, **kwargs):
#         try:
#             return super().update(request, *args, **kwargs)
#         except Exception as e:
#             return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             return super().destroy(request, *args, **kwargs)
#         except Exception as e:
#             return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)
