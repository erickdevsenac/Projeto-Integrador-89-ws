from django.db import models

class EquipeDev(models.Model):
    nome = models.CharField(max_length=80, null=False)
    link_git = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nome
    
