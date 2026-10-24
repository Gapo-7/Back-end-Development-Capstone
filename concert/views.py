from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.conf import settings
import json
import os
from pathlib import Path

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": form})


def index(request):
    return render(request, "index.html")


def songs(request):
    endpoint = os.environ.get("SONGS_SERVICE_URL", "http://127.0.0.1:8081")
    try:
        response = req.get(f"{endpoint.rstrip('/')}/song", timeout=5)
        response.raise_for_status()
        song_list = response.json()
    except (req.RequestException, ValueError):
        song_list = []
    return render(request, "songs.html", {"songs": song_list})


def photos(request):
    endpoint = os.environ.get("PICTURES_SERVICE_URL", "http://127.0.0.1:8080")
    try:
        response = req.get(f"{endpoint.rstrip('/')}/picture", timeout=3)
        response.raise_for_status()
        photo_list = response.json()
    except (req.RequestException, ValueError):
        snapshot = Path(__file__).resolve().parent / "data" / "pictures.json"
        photo_list = json.loads(snapshot.read_text(encoding="utf-8"))
    return render(request, "photos.html", {"photos": photo_list})

def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse("index"))
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def concerts(request):
    concert_list = []
    for concert in Concert.objects.order_by("date"):
        attending = None
        if request.user.is_authenticated:
            attending = ConcertAttending.objects.filter(
                concert=concert, user=request.user
            ).first()
        concert_list.append({
            "concert": concert,
            "status": attending.attending if attending else "-",
        })
    return render(request, "concerts.html", {"concerts": concert_list})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = get_object_or_404(Concert, pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
