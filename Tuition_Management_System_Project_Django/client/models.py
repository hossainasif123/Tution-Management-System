from django.db import models
from tuition.models import Ad


class ClientFeedback(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    rating = models.IntegerField(verbose_name='Rating')
    feedback = models.TextField(verbose_name='Feedback')

    def __str__(self):
        return self.ad.title
