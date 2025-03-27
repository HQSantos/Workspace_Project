import requests
from app_main.utils.logger import log_error
from datetime import datetime
from .models import Cotacao
from datetime import date, timedelta

API_URL = "https://api.vatcomply.com/rates" #constante para evitar longas strings

def consultar_dia_util(data):
    """
    Retorna True se a data for um dia útil (segunda a sexta-feira).
    """
    return data.weekday() < 5  # 0 = segunda, 4 = sexta

def obter_cotacoes():
    try:
        response = requests.get(f"{API_URL}?base=USD")
        response.raise_for_status()
        data = response.json()

        data_cotacao = datetime.strptime(data["date"], "%Y-%m-%d").date()

        if not consultar_dia_util(data_cotacao):
            print("Cotação recebida em um dia não útil. Ignorando...")
            return  # Ignorar cotacoes em fins de semana ou feriados

        moedas_interessadas = ["BRL", "EUR", "JPY"]

        for moeda in moedas_interessadas:
            valor = data["rates"].get(moeda)
            if valor:
                Cotacao.objects.update_or_create(
                    moeda=moeda,
                    data=data_cotacao,
                    defaults={"valor": valor}
                )

        # Limpar cotacoes antigas mantendo apenas os ultimos 5 dias uteis
        cotacoes_existentes = Cotacao.objects.values_list("data", flat=True).distinct().order_by("-data")

        dias_uteis = [dia for dia in cotacoes_existentes if consultar_dia_util(dia)]
        if len(dias_uteis) > 5:
            dias_a_excluir = dias_uteis[5:]  # Mantem os 5 dias mais recentes
            Cotacao.objects.filter(data__in=dias_a_excluir).delete()

        print("Cotações atualizadas com sucesso!")
        
    except requests.Timeout:
        log_error("Timeout ao tentar acessar a API.")
    except requests.RequestException as e:
        log_error("Erro ao buscar cotações", e)
    except Exception as e:
        log_error("Erro inesperado", e)
