from django.test import TestCase

from django.test import TestCase, Client
from datetime import datetime
from .views import obter_dias_uteis_semana, gerar_grafico
from .models import Cotacao

class CotacaoTestCase(TestCase):
    def setUp(self):
        """Cria dados iniciais no banco de teste"""
        Cotacao.objects.create(moeda="BRL", data="2025-03-24", valor=5.12)
        Cotacao.objects.create(moeda="EUR", data="2025-03-25", valor=1.08)
        Cotacao.objects.create(moeda="JPY", data="2025-03-26", valor=150.45)

    def test_obter_dias_uteis(self):
        """Testa se os dias úteis são retornados corretamente"""
        dias_uteis = obter_dias_uteis_semana("2025-03-26")
        self.assertEqual(len(dias_uteis), 5)  # Deve retornar 5 dias úteis

    def test_gerar_grafico(self):
        """Testa se o gráfico é gerado corretamente"""
        dias_uteis = ["2025-03-24", "2025-03-25", "2025-03-26"]
        moedas = ["BRL", "EUR", "JPY"]
        grafico = gerar_grafico(dias_uteis, moedas)
        self.assertIn("data:image/png;base64,", grafico)  # Deve gerar um gráfico em Base64

    def test_view_grafico(self):
        """Testa se a página do gráfico carrega corretamente"""
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")  # Deve conter uma imagem no HTML (o gráfico)
