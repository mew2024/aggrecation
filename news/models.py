from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(max_length=200)
    article_url = models.URLField(max_length=500)  # 掲載元URLを保存
    source = models.CharField(max_length=100, blank=True)  # 掲載元サイト名など
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ViewingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    article_url = models.URLField(default='')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.article_url}"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'url')
        ordering = ['-created_at']