from django.forms import ModelForm
from django import forms
from .models import Auction

class AuctionForm(forms.ModelForm):
    
    class Meta:
        model = Auction
        fields = ['title', 'description', 'image', 'current_bid','expiration_date',]