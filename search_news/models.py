from django.db import models
from django.contrib.auth.models import User, AbstractUser


# Create your models here.

class newsUser(AbstractUser):
    # user = models.ForeignKey(newsUser, on_delete=models.CASCADE)
    quota = models.IntegerField(default=0)


class searchHistory(models.Model):
    user = models.ForeignKey(newsUser, on_delete=models.CASCADE)
    search_str = models.TextField()
    count = models.IntegerField(default=1)
    total_results = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.search_str
    
    class Meta:
        verbose_name = "Search history"


class newsArticle(models.Model):
    search = models.ForeignKey(searchHistory, on_delete=models.CASCADE)
    author = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    url = models.URLField(null=True)
    urlToImage = models.URLField(null=True)
    language = models.CharField(max_length=50, null=True)
    category = models.CharField(max_length=100, null=True)
    source = models.CharField(max_length=100, null=True)
    publishedAt = models.DateTimeField(null=True)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "News Article"
