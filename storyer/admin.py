from django.contrib import admin

# Register your models here.

from .models import Student, Assignment

admin.site.register(Student)
admin.site.register(Assignment)
