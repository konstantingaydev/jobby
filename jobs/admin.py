from django.contrib import admin

# Register your models here.
from .models import Job
class JobAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
admin.site.register(Job, JobAdmin)