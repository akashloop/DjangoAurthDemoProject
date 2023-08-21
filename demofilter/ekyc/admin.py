from django.contrib import admin
from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportExportModelAdmin



# Register your models here.
from .models import *
admin.site.register(Document)
# admin.site.register(KYCKYBEntry)


class KYCKYBEntryResource(resources.ModelResource):
    first_name = Field(attribute='first_name', column_name='Name')
    class Meta:
        model = KYCKYBEntry
        fields = ('id', 'user', 'first_name', 'last_name', 'dob')
        export_order = ('id', 'user', 'last_name', 'dob','first_name',)

class KYCKYBEntryAdmin(ImportExportModelAdmin):
    resource_class = KYCKYBEntryResource
admin.site.register(KYCKYBEntry, KYCKYBEntryAdmin)



