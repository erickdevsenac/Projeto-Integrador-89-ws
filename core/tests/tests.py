from django.test import TestCase
from django.urls import reverse


class MeusTestes(TestCase):
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
    
    def test_pacote_carrega_corretamente(self):
        home = reverse("core:pacote")
        self.assertEqual(home, '/pacote/')   
    
    def test_perfil_carrega_corretamente(self):
        home = reverse("core:perfil")
        self.assertEqual(home, '/perfil/')
    
    def test_avaliacao_carrega_corretamente(self):
        home = reverse("core:avaliacao")
        self.assertEqual(home, '/avaliacao/')           
    
    def test_nova_avaliacao_carrega_corretamente(self):
        home = reverse("core:nova_avaliacao")
        self.assertEqual(home, '/nova_avaliacao/')

    def test_configuracoes_carrega_corretamente(self):
        home = reverse("core:configuracoes")
        self.assertEqual(home, '/configuracoes/')
 