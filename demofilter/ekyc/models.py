from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django_extensions.db.models import TimeStampedModel
from location.models import Country



class Document(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=100, unique=True,) 
    country = models.ForeignKey(Country, on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return str(self.name)


class KYCKYBEntry(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    first_name =  models.CharField(max_length=100,null=True, blank=True)
    last_name = models.CharField(max_length=100,null=True, blank=True)
    dob = models.CharField(max_length=100,null=True, blank=True)
    doc_number = models.CharField(max_length=100,null=True, blank=True)
    doc_image = models.FileField("Document Image", upload_to="Document_image",null=True, blank=True)
    company_name = models.CharField(max_length=255,null=True, blank=True )
    email_address = models.CharField(max_length=150,null=True, blank=True)
    business_registreation_no = models.CharField(max_length=100,null=True, blank=True)
    doc_expiry_date = models.DateField(null=True, blank=True)
    documents= models.ManyToManyField(Document,verbose_name="Documents", related_name="kyc_kyb_doc", blank=True,through="CountryDocument",)
    verification_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],default='pending' )
    

    def __str__(self):
        return str(self.id)

class CountryDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE,null=True, blank=True)
    kyckyb = models.ForeignKey(KYCKYBEntry, on_delete=models.CASCADE,null=True, blank=True)
    class Meta:
        unique_together = (("document", "kyckyb"),)
        
    def __str__(self):
        return str(self.document.name)




    