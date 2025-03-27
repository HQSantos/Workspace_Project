from django.urls import path
from .views import obter_grafico_cotacoes, exibir_grafico

urlpatterns = [
    path("grafico/", obter_grafico_cotacoes, name="grafico"),  
    path("grafico/exibir/", exibir_grafico, name="exibir_grafico"),  
]
