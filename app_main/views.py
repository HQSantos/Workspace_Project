import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import urllib
import base64
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from datetime import date, datetime, timedelta
from .models import Cotacao
from .services import obter_cotacoes_para_semana

def obter_grafico_cotacoes(request):
    # Obtém os últimos 5 dias úteis
    hoje = datetime.today().date()
    dias_uteis = []
    while len(dias_uteis) < 5:
        if hoje.weekday() < 5:  
            dias_uteis.append(hoje)
        hoje -= timedelta(days=1)

    dias_uteis.reverse()

    moedas = ["BRL", "EUR", "JPY"]
    dados = {moeda: [] for moeda in moedas}

    for dia in dias_uteis:
        for moeda in moedas:
            cotacao = Cotacao.objects.filter(data=dia, moeda=moeda).first()
            valor = cotacao.valor if cotacao else None
            dados[moeda].append(valor)

    plt.figure(figsize=(8, 5))
    for moeda, valores in dados.items():
        plt.plot(dias_uteis, valores, marker="o", label=moeda)

    plt.xlabel("Data")
    plt.ylabel("Cotação")
    plt.title("Cotações dos últimos 5 dias úteis")
    plt.legend()
    plt.grid(True)

    # Salvar imagem em buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Converter imagem para URL
    image_png = buffer.getvalue()
    buffer.close()

    return HttpResponse(image_png, content_type="image/png")
     

def obter_ultimos_dias_uteis(qtd_dias=5):
    """ Retorna uma lista com as datas dos últimos N dias úteis."""
    datas = []
    hoje = datetime.today().date()
    while len(datas) < qtd_dias:
        if hoje.weekday() < 5:  # Segunda (0) a Sexta (4) sao dias úteis
            datas.append(hoje)
        hoje -= timedelta(days=1)
    return sorted(datas)

def gerar_grafico(dias_uteis, moedas, cotacoes):
    plt.figure(figsize=(8, 5))

    for moeda in moedas:
        valores = [cotacoes[d].get(moeda) for d in dias_uteis]

        plt.plot(dias_uteis, valores, marker='o', label=moeda)

        # Adiciona os valores acima de cada ponto
        for i, valor in enumerate(valores):
            if valor is not None:
                plt.text(dias_uteis[i], valor, f"{valor:.2f}", fontsize=10, ha='center', va='bottom')

    plt.xlabel("Dias da semana")
    plt.ylabel("Cotação (USD)")
    #formatacao das datas para o padrao dd/mm/aaaa
    data_inicio = datetime.strptime(dias_uteis[-1], "%Y-%m-%d").strftime("%d/%m/%Y")
    data_fim = datetime.strptime(dias_uteis[0], "%Y-%m-%d").strftime("%d/%m/%Y")

    plt.title(f"Cotações de {data_inicio} a {data_fim}")
    plt.xticks(dias_uteis, [datetime.strptime(d, "%Y-%m-%d").strftime("%a") for d in dias_uteis])
    plt.legend()
    plt.grid()

    # Salvar imagem como base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return f"data:image/png;base64,{img_str}"

def obter_dias_uteis_semana(data_referencia):
    if not isinstance(data_referencia, datetime):
        try:
            data_referencia = datetime.strptime(data_referencia, "%Y-%m-%d")
        except ValueError:
            print("Erro ao converter data. Usando hoje como referência.")
            data_referencia = datetime.today()

    dias_uteis = []
    data_temp = data_referencia

    while len(dias_uteis) < 5:
        if data_temp.weekday() < 5:  
            dias_uteis.append(data_temp.strftime("%Y-%m-%d"))
        data_temp -= timedelta(days=1)

    print("Dias úteis calculados:", dias_uteis)  # Depuracao
    return dias_uteis

def exibir_grafico(request):
    """ View para exibir o gráfico no template com base na data e moedas selecionadas. """

    data_selecionada = request.GET.get("data", datetime.today().strftime("%Y-%m-%d"))

    dias_uteis = obter_dias_uteis_semana(data_selecionada)

    moedas_selecionadas = request.GET.getlist("moedas")
    if not moedas_selecionadas:
        moedas_selecionadas = ["BRL", "EUR", "JPY"]

    cotacoes = obter_cotacoes_para_semana(data_selecionada)

    grafico_url = gerar_grafico(dias_uteis, moedas_selecionadas, cotacoes)

    return render(request, "grafico.html", {
        "grafico_url": grafico_url,
        "data_selecionada": data_selecionada,
        "moedas_selecionadas": moedas_selecionadas
    })

