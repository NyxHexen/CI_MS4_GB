from django.db import models

# Create your models here.

class Game(models.Model):

    name = models.CharField(max_length=254)
    slug = models.CharField(max_length=254)
    genre = models.ManyToManyField('Genre')
    publisher = models.ForeignKey('Publisher')
    developers = models.ManyToManyField('Developer')
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    rating = models.ForeignKey('Rating', on_delete=models.SET_NULL)
    platform = models.ManyToManyField('Platform')
    tags = models.ManyToManyField('Tag')
    screenshots = models.ForeignKey('Screenshot', null=True)
    dlc = models.ForeignKey('DLC', null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return self.slug

    def get_friendly_name(self):
        return self.name






