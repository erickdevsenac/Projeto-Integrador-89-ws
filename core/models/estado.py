from django.db import models
from core.static import estado

nome = estado.UF
class Estados(models.Model):
    estado = models.CharField(max_length=2, choices= nome)
