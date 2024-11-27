from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class Filme(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    data_lancamento = models.DateField()
    id = models.CharField(max_length=15, unique=True, primary_key= True)
    poster = models.URLField(max_length=255, blank=True, null=True) 
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Review(models.Model):
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    avaliacao = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,  # permite valores nulos
        blank=True  # permite que o campo seja deixado em branco no formulário  # avaliação de 1 a 5 estrelas
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.filme.titulo}'


