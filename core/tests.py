from django.test import TestCase
from django.urls import reverse

class test_geral(TestCase):
    def test_primeiro(self):
        assert 1 == 1

        def test_home_carrega_corretamente(self):
            home = reverse("core:index")
            self.assertEqual(home, '/')

        def test_perfil_carrega_corretamente(self):
            home = reverse("core:perfil")
            self.assertEqual(home,'/perfil/')    

        def test_produtos_carrega_corretamente(self):
            home = reverse("core:produtos")
            self.assertEqual(home, '/produtos/')      
