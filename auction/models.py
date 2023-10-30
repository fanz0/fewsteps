from django.db import models
from django.utils import timezone

class Auction(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField()
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    current_bid = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['created_at']
        
