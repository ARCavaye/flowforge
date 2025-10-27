from django.db import models

# Create your models here.


class venue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    riskAssessmentUrl = models.URLField()

    def __str__(self):
        return self.name
