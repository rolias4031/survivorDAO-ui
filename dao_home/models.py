from django.db import models

# Create your models here.
class Project(models.Model):
    img = models.ImageField(upload_to='dao_home/images/')
