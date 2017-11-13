from django.contrib import admin

# Register your models here.
from .models import ModelType,LabItemMaterial,CreatedModelUse

admin.site.register(ModelType)
admin.site.register(LabItemMaterial)
admin.site.register(CreatedModelUse)