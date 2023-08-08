from django.db import models
import uuid
from django.contrib import admin

# import abstract modules

from account.models import Currency 
from django_extensions.db.models import TimeStampedModel


class Country(TimeStampedModel):
    country = models.CharField(max_length=50,unique=True,db_index=True)
    iso_code = models.CharField(max_length=50,unique=True,db_index=True)
    isd = models.CharField(max_length=5,unique=True,db_index=True)
    currency = models.ForeignKey(Currency,related_name="currency_country", on_delete=models.SET_NULL,blank=True, null=True,)
    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        db_table = "Country"

    def __str__(self):
        return self.country
