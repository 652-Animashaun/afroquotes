from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django import forms
import json
import datetime
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from djrichtextfield.widgets import RichTextWidget

from .models import *


# Create your views here.
class SubmitQuote(forms.Form):
	quote = forms.CharField(widget=forms.Textarea())
	song = forms.CharField(max_length=64)
	artist= forms.CharField(max_length=64)
	image = forms.URLField()

class Annotate(forms.Form):
	annotation=forms.CharField(max_length=300)
class searchForm(forms.Form):
    queryTerm= forms.CharField(max_length=32)


def index(request):
    if request.method=="POST":
        form = searchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['queryTerm']

            results = Quote.objects.filter(quote__icontains=query)
            return render(request, "afroquotes/index.html", {
                "form": searchForm(),
                "Quotes": results
                })
    else:
    	Quotes = Quote.objects.all().order_by("-timestamp")


    	return render(request, "afroquotes/index.html", {
    		"Quotes": Quotes,
            "form": searchForm()
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
            quoteAnnotQuery.last_viewed=datetime.now()
            quoteAnnotQuery.annotation_view_count+=1
            quoteAnnotQuery.save()
            print(quoteAnnotQuery)
        except Annotation.DoesNotExist:
            # returning error to fetch request from JS. This is deprecated. Now render without JSON
            # return JsonResponse({"Error": "There are no annotations for this Quote."}, status=404)
            return render(request, "afroquotes/quote.html", {
                "quote": quote,
                "notfoundError": "There are no annotations for this Quote."
                })
        # return JsonResponse(quoteAnnotQuery.serialize())
        sQuotes= Quote.objects.filter(song=quote.song, artist=quote.artist)
        aQuotes= Quote.objects.filter(artist=quote.artist)
        annotationSugg = SuggestionComment.objects.filter(annotation=quoteAnnotQuery)

        return render (request, "afroquotes/quote.html", {
            "quote":quote,
            "annotationSugg":annotationSugg,
            "annotation": quoteAnnotQuery,
            "sQuotes": sQuotes,
            "aQuotes":aQuotes
            })
    else:
        return render(request, "afroquotes/login.html")

def write_annotate(request, quote_id):
    quote_id = int(quote_id)
    annotated = Quote.objects.get(id=quote_id)
    if request.method=='POST':
            if request.user.is_authenticated:
                form = Annotate(request.POST)
                print(form)

                if form.is_valid():
                    annotation = form.cleaned_data['annotation']
                    print(annotation)
                    annotator= request.user
                    annotate = Annotation(annotation=annotation, annotator=annotator, annotated=annotated)
                    annotate.save()
                    return render(request, "afroquotes/annotation.html",{
                        "form":Annotate(),
                        "quote": annotated,
                        "annotations": Annotation.objects.filter(annotated=annotated)
                        })
            else:
                return HttpResponseRedirect (reverse('login'))
    else:
        return render(request, "afroquotes/annotation.html", {
            "form": Annotate(),
            "quote": annotated
            })

# More from artist or song || artist and song
# Should also work for filter by artist, song
# In anyway, user click artist or song title to fetch more..

def quote_by(request, filt_term):

    quote_by_art = Quote.objects.filter(artist=filt_term).order_by("-timestamp")

    return render( request, "afroquotes/index.html", {
        "Quotes":quote_by_art
        })

def quote_from(request, filt_term):

    quote_from_song = Quote.objects.filter(song=filt_term)

    return render( request, "afroquotes/index.html", {
        "Quotes":quote_from_song
        })

@csrf_exempt

def upvote(request, annoid):
    if request.user.is_authenticated:
        
        if request.method == 'POST':
            # data = json.loads(request.body)
            # print(data)
            

            user = request.user
            # annoid = data.get("annotation")
            
            
            
            annotation = Annotation.objects.get(id=annoid)
            print(annotation.annotated.id)

            pre_upvoted = Upvote.objects.filter(user=user, annotation=annotation)
            if not pre_upvoted:
                upvote = Upvote(annotation=annotation, user=user)
                upvote.save()

            else:
                upvote = Upvote.objects.filter(annotation=annotation, user=user)
                upvote[0].delete()
                

            return HttpResponseRedirect(reverse("annotate", args=(annotation.annotated.id,)))
        else:
            return HttpResponseRedirect(reverse("annotate", args=(annotation.annotated.id,)))
    else:
        return render(request, "afroquotes/login.html")


@csrf_exempt
def submitSuggestion(request, annoID):
    if request.user.is_authenticated:
        if request.method=='POST':
            user = request.user
            data = json.loads(request.body)
            suggested = data["submitedSugg"].strip()
            # annoid = int(data["annotationID"])
            try:
                annotation= Annotation.objects.get(id=annoID)
                suggestioncomm = SuggestionComment(user=user, annotation=annotation, suggestion=suggested)
                suggestioncomm.save()
                return JsonResponse({"suggested":suggestioncomm.serialize()}, status=201)

            except Annotation.DoesNotExist:
                return JsonResponse({"message": "not found" }, status=500)
        else:
            return JsonResponse({"message":"method not allowed"}, status=400)
    else:
        return JsonResponse({"message":"Please login to help us make this annotation better!"})

        









