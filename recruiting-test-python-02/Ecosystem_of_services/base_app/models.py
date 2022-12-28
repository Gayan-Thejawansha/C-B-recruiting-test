from django.db import models

# Create your models here.

class Investor(models.Model):
    name = models.CharField(max_length=200, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.TextField(null=True)
    description = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated', '-added']

    def __str__(self):
        return self.name
