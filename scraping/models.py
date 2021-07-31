from django.db import models

class Search(models.Model):
    place = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
