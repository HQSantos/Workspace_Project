from django.test import TestCase
from unittest.mock import patch
from app_main.services import obter_cotacoes
from app_main.models import Cotacao

class CotacaoServiceTest(TestCase):
    @patch("app_main.services.requests.get")
    def test_obter_cotacoes_sucesso(self, mock_get):
        # Simular um JSON de resposta da API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "date": "2025-03-23",
            "base": "USD",
            "rates": {
                "BRL": 5.20,
                "EUR": 0.92,
                "JPY": 130.5
            }
        }

        obter_cotacoes()

        # Validar os dados da Cotacao
        self.assertEqual(Cotacao.objects.count(), 3)
        self.assertEqual(Cotacao.objects.get(moeda="BRL").valor, 5.20)
        self.assertEqual(Cotacao.objects.get(moeda="EUR").valor, 0.92)
        self.assertEqual(Cotacao.objects.get(moeda="JPY").valor, 130.5)
