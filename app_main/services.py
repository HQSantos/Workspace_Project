import requests
from .log_config import logger 
from datetime import datetime
from .models import Cotacao

API_URL = "https://api.vatcomply.com/rates" #constante para evitar longas strings

def obter_cotacoes():
    """
    Buscar as cotações do dólar para BRL, EUR e JPY para salvar na base.
    """
    try:
        response = requests.get(f"{API_URL}?base=USD")
        response.raise_for_status()
        data = response.json()

        data_cotacao = datetime.strptime(data["date"], "%Y-%m-%d").date()
        moedas_interessadas = ["BRL", "EUR", "JPY"] #filtrando apenas as moedas requeridas

        for moeda in moedas_interessadas:
            valor = data["rates"].get(moeda)
            if valor:
                Cotacao.objects.update_or_create(
                    moeda=moeda,
                    data=data_cotacao,
                    defaults={"valor": valor}
                )

        logger.info("Cotações obtidas com sucesso!")

    except requests.Timeout:
        logger.error("Timeout ao tentar acessar a API.")
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar cotações: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
