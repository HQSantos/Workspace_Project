from django.db import models

from django.db import models

class Cotacao(models.Model):
    moeda = models.CharField(max_length=3) #Colocado o maximo de campos como 3 pensando no US$, EUR e JPY
    valor = models.DecimalField(max_digits=10, decimal_places=4) #Valor da moeda
    data = models.DateField() #data de cotacao

    class Meta:
        unique_together = ('moeda', 'data')  

    def __str__(self):
        return f"{self.moeda} - {self.valor} ({self.data})"
