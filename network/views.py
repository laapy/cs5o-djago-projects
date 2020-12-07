from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import json

from .models import User, Posts


def index(request):
    return render(request, "network/index.html")


def post_update(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = json.loads(request.body)
            p = Posts(post=data['post'], uploaded_by=request.user)
            p.save()
            return JsonResponse({'successfull': True}, status=200)
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))


def update_followers(request, verb):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = json.loads(request.body)
            r_user = User.objects.filter(username=str(data['uname'])).first()
            print(r_user,data)
            if r_user != None:
                if str(verb) == 'follow':
                    request.user.following.add(r_user)
                    r_user.followers.add(request.user)
                    return JsonResponse({'successfull': True}, status=200)
                elif str(verb) == 'unfollow':
                    request.user.following.remove(r_user)
                    r_user.followers.remove(request.user)
                    return JsonResponse({'successfull': True}, status=200)
                else:
                    return JsonResponse({'successfull': False}, status=200)
            else:
                return JsonResponse({'successfull': False}, status=200)
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))


def posts(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            posts = Posts.objects.order_by("-created_on").all()
            return render(request, "network/posts.html",
                          {'posts': posts}
                          )
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))

def following_list(request,name):
    if request.method == "GET":
        if request.user.is_authenticated:

            user = User.objects.filter(username=str(name)).first()
            following_list = list(user.following.values_list('username',flat=True))
            all = request.user == user
            if all:
                return JsonResponse({'users':following_list,'all': all},status=200)
            else:
                follows= [request.user.following.filter(username=name).exists() for name in following_list]
                return JsonResponse({'users':following_list,'all': all,'if_loogedIn_user_follows':follows},status=200)
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))

def follower_list(request,name):
    if request.method == "GET":
        if request.user.is_authenticated: 
            user = User.objects.filter(username=str(name)).first()
            follower_list = list(user.followers.values_list('username',flat=True))
            follows= [request.user.following.filter(username=name).exists() for name in follower_list]
            return JsonResponse({'users':follower_list,'if_loogedIn_user_follows':follows,'all':False},status=200)
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))

def user_profile(request, name):
    if request.method == "GET":
        if request.user.is_authenticated:

            r_user = User.objects.filter(username=str(name)).first()
            # print(user)
            if r_user != None:

                return render(request, "network/profile_page.html",
                              {'ruser': r_user,
                               'already_follows': request.user.following.filter(pk=r_user.pk).exists()
                              })
            else:
                return JsonResponse({'successfull': False})
        else:
            return redirect((reverse("login")))
    else:
        return redirect((reverse("index")))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
