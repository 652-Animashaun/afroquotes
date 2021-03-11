from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse

from .models import *


# Create your views here.
class SubmitQuote(forms.Form):
	quote = forms.CharField(max_length=500)
	song = forms.CharField(max_length=64)
	artist= forms.CharField(max_length=64)
	image = forms.URLField()

class Annotate(forms.Form):
	annotation=forms.CharField(max_length=300)
class search(forms.Form):
    queryTerm= forms.CharField(max_length=32)


def index(request):
    if request.method=="POST":
        query = request.POST["query"]
        print(query)
        pass

    else:

    	Quotes = Quote.objects.all()

    	return render(request, "afroquotes/index.html", {
    		"Quotes": Quotes,
            "form": search()
    		})


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "afroquotes/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "afroquotes/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "afroquotes/register.html")

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
            return render(request, "afroquotes/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "afroquotes/login.html")
# def search(request, query):
#     if request.method=="POST":
#         query = request.POST["query"].strip()
#         query = query.split(",")



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def submitQuote(request):
	if request.user.is_authenticated:
		if request.method=='POST':
			form = SubmitQuote(request.POST)
			if form.is_valid():
				quote = form.cleaned_data['quote']
				artist = form.cleaned_data['artist']
				song = form.cleaned_data['song']
				image = form.cleaned_data['image']

				contributor=request.user

				quote = Quote(quote=quote, artist=artist, song=song, image=image, contributor=contributor)
				quote.save()
				return render(request, "afroquotes/index.html")
		return render(request, "afroquotes/submitQuote.html", {
			"form":SubmitQuote()
			})
	return render(request, "afroquotes/login.html")


def annotate(request, quote_id):

    # query for requested qoute
    try:
        quote = Quote.objects.get(id=quote_id)
    except Quote.DoesNotExist:
        return JsonResponse({"error": "quote not found"}, status=404)
    if request.method == "GET":
        try:
            quoteAnnotQuery = Annotation.objects.get(annotated=quote)
        except Annotation.DoesNotExist:
            return JsonResponse({"Error": "There are no annotations for this Quote."}, status=404)
        return JsonResponse(quoteAnnotQuery.serialize())
 
    # if request.user.is_authenticated:
    #     annotator = request.user
    #     annotated = Quote.objects.get(id=quote_id)
        
        if request.method=='POST':
            form = Annotate(request.POST)
            if form.is_valid():
                annotation = form.cleaned_data['annotation']
                
                annotate = Anotation(annotation=annotation, annotator=annotator, annotated=annotated)
                annotate.save()
                return render(request, "afroquotes/annotation.html",{
                    "form":Annotate(),
                    "quote": annotated,
                    "annotations": Anotation.objects.filter(annotated=annotated)
                    })

                # trying to remove replace this route with json response and modal display
        # else:
        #     return render(request, "afroquotes/annotation.html", {
        #             "form":Annotate(),
        #             "quote": annotated,
        #             "annotations": Anotation.objects.filter(anotated=annotated)
        #         })
    else:
        return render(request, "afroquotes/login.html")