from django.db import models


class Search(models.Model):
    psc = models.CharField(max_length=100)
    distance = models.CharField(max_length=100)
    choice = models.CharField(max_length=100)
