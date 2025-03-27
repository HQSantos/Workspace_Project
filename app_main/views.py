import matplotlib.pyplot as plt
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

def gerar_grafico():
    """Gera um gráfico de cotações usando Matplotlib e retorna a URL da imagem."""
    dias_uteis = obter_ultimos_dias_uteis()
    moedas = ["BRL", "EUR", "JPY"]
    
    plt.figure(figsize=(8, 5))
    for moeda in moedas:
        valores = [Cotacao.objects.filter(moeda=moeda, data=d).first() for d in dias_uteis]
        valores = [c.valor if c else None for c in valores]
        plt.plot(dias_uteis, valores, marker='o', label=moeda)
    
    plt.xlabel("Data")
    plt.ylabel("Cotação (USD)")
    plt.title("Cotações dos últimos 5 dias úteis")
    plt.legend()
    plt.grid()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    
    return f"data:image/png;base64,{img_str}"

def exibir_grafico(request):
    """ View para exibir o gráfico no template."""
    grafico_url = gerar_grafico()
    return render(request, "grafico.html", {"grafico_url": grafico_url})
