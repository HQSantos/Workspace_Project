from django.test import TestCase
from unittest.mock import patch
from datetime import date, timedelta
from app_main.models import Cotacao
from app_main.services import obter_cotacoes

class CotacaoServiceTest(TestCase):
    def setUp(self):
        """
        Configuração inicial: cria cotações para 7 dias úteis anteriores.
        """
        self.moedas = ["BRL", "EUR", "JPY"]

        # Criar cotações para 7 dias úteis anteriores
        data_atual = date.today()
        dias_uteis = []
        while len(dias_uteis) < 7:
            if data_atual.weekday() < 5:  # Segunda a sexta-feira
                dias_uteis.append(data_atual)
            data_atual -= timedelta(days=1)  # Volta um dia

        for data in dias_uteis:
            for moeda in self.moedas:
                Cotacao.objects.create(moeda=moeda, data=data, valor=5.0)

    @patch("app_main.services.requests.get")
    def test_limita_cinco_dias_uteis(self, mock_get):
        """
        Testa se o sistema mantém apenas os últimos 5 dias úteis após obter novas cotações.
        """
        # Simula uma nova cotação recebida da API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "date": str(date.today()),
            "base": "USD",
            "rates": {"BRL": 5.20, "EUR": 0.92, "JPY": 130.5}
        }

        obter_cotacoes()  # Chama a função que deve limpar os dias extras

        # Conta quantos dias únicos ainda existem no banco
        dias_no_banco = Cotacao.objects.values_list("data", flat=True).distinct()
        
        # Verifica se apenas 5 dias úteis foram mantidos
        self.assertEqual(len(dias_no_banco), 5, "O banco deve manter apenas os últimos 5 dias úteis")
