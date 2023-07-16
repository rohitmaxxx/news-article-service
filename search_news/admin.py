from django.contrib import admin
from .models import newsArticle, searchHistory, newsUser

# Register your models here.
admin.site.register((newsArticle, searchHistory, newsUser))