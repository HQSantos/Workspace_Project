import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import urllib
import base64
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from datetime import date, datetime, timedelta
from .models import Cotacao

def obter_grafico_cotacoes(request):
    # Obtém os últimos 5 dias úteis
    hoje = datetime.today().date()
    dias_uteis = []
    while len(dias_uteis) < 5:
        if hoje.weekday() < 5:  # 0 = Segunda-feira, 4 = Sexta-feira
            dias_uteis.append(hoje)
        hoje -= timedelta(days=1)

    dias_uteis.reverse()

    # Busca cotações no banco
    moedas = ["BRL", "EUR", "JPY"]
    dados = {moeda: [] for moeda in moedas}

    for dia in dias_uteis:
        for moeda in moedas:
            cotacao = Cotacao.objects.filter(data=dia, moeda=moeda).first()
            valor = cotacao.valor if cotacao else None
            dados[moeda].append(valor)

    # Criar o gráfico
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
        if hoje.weekday() < 5:  # Segunda (0) a Sexta (4) são dias úteis
            datas.append(hoje)
        hoje -= timedelta(days=1)
    return sorted(datas)

def gerar_grafico(data, moedas):
    plt.figure(figsize=(8, 5))

    for moeda in moedas:
        valores = [Cotacao.objects.filter(moeda=moeda, data=d).first() for d in dias_uteis]
        valores = [c.valor if c else None for c in valores]
        
        plt.plot(dias_uteis, valores, marker='o', label=moeda)

    plt.xlabel("Dias da semana")
    plt.ylabel("Cotação (USD)")
    plt.title(f"Cotações da semana {dias_uteis[0].strftime('%d/%m/%Y')} - {dias_uteis[-1].strftime('%d/%m/%Y')}")
    plt.xticks(dias_uteis, [d.strftime("%a") for d in dias_uteis])  # Exibir Seg, Ter, Qua...
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
    dias_uteis = []
    for i in range(5):
        dia = data_referencia - timedelta(days=i)
        if dia.weekday() < 5: 
            dias_uteis.append(dia.strftime("%Y-%m-%d"))
    return dias_uteis[::-1]

def exibir_grafico(request):
    """ View para exibir o gráfico no template com base na data e moedas selecionadas. """
    data_str = request.GET.get("data")  #obtem a data como string
    
    try:
        data_selecionada = datetime.strptime(data_str, "%Y-%m-%d") if data_str else datetime.today()
    except ValueError:
        data_selecionada = datetime.today()  #Se houver erro na conversao, usa a data atual

    dias_uteis = obter_dias_uteis_semana(data_selecionada)

    #captura as moedas selecionadas (se nenhuma for selecionada, assume todas)
    moedas_selecionadas = request.GET.getlist("moedas")
    if not moedas_selecionadas:
        moedas_selecionadas = ["BRL", "EUR", "JPY"]

    grafico_url = gerar_grafico(dias_uteis, moedas_selecionadas)

    return render(request, "grafico.html", {
        "grafico_url": grafico_url,
        "data_selecionada": data_selecionada.strftime("%Y-%m-%d"),  
        "moedas_selecionadas": moedas_selecionadas
    })