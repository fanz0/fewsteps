from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .forms import CreateUserForm, BioEditForm
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6379,db=0)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_page')
        else:
            messages.success(request, ('There was an error loggin in, try again..'))
            return redirect('login_user')
    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('You were logged out!'))
    return redirect('home_page')

def register_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successfull!"))
            profile = Profile()
            profile.user = request.user
            profile.save()
            return redirect('home_page')
    else:
        form = CreateUserForm()
    return render(request, 'authenticate/register_user.html', {'form':form})

@login_required
def profile(request):
    profile_user = Profile.objects.get(user=request.user)
    profile_bio = profile_user.bio
    lunghezza = len(client.keys())
    sneakers = []
    prices = []
    auctions = []
    hashes = []
    for x in range(lunghezza):
        if client.hget(client.keys()[x], "Vincitore"):
            if client.hget(client.keys()[x], "Vincitore").decode("utf-8") == str(Profile.objects.get(user=request.user)) :
                sneakers.append(client.keys()[x].decode("utf-8"))
                prices.append(client.hget(client.keys()[x], "Prezzo").decode("utf-8"))
                auctions.append(client.hget(client.keys()[x], "Asta").decode("utf-8"))
                hashes.append(client.hget(client.keys()[x], "Hash Transazione").decode("utf-8"))
    return render(request, 'authenticate/profile.html', {'bio':profile_bio, 'sneakers': sneakers, 'prices': prices, 'auctions': auctions, 'hashes': hashes})

def bio_edit(request):
    if request.method == 'POST':
        form = BioEditForm(request.POST, request.FILES)
        if form.is_valid():
            new_bio = form.cleaned_data['bio']
            profile = Profile.objects.get(user=request.user)
            profile.bio = new_bio
            profile.save()
            return redirect('profile_user')
    else:
        form = BioEditForm()
    return render(request, 'bio_edit.html', {})
