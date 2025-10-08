from django.db import models

class EquipeDev(models.Model):
    nome = models.CharField(max_length=80, null=False)
    foto = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None)
    link_git = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nome
    
