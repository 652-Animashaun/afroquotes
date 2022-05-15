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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import *


# Create your views here.
# class SubmitQuote(forms.Form):
# 	quote = forms.CharField(widget=forms.Textarea())
# 	song = forms.CharField(max_length=64)
# 	artist= forms.CharField(max_length=64)
# 	image = forms.URLField()

class Annotate(forms.Form):
	annotation=forms.CharField(max_length=300)
class searchForm(forms.Form):
	queryTerm= forms.CharField(max_length=32)


def index(request):
	return render(request, "afroquotes/index_js.html")

def all_quotes(request):
	quotes = Quote.objects.all().order_by("-timestamp")
	page_num = request.GET.get('page')

	paginator = Paginator(quotes, 3)
	try:
		page_obj= paginator.get_page(page_num)

	except PageNotAnInteger:
		page_obj= {'error', 'Invalid Page'}

	except EmptyPage:
		page_obj = paginator.get_page(1)


	if page_obj.has_next():
		page_obj_next = page_obj.next_page_number()
	else:
		page_obj_next = 1

	if page_obj.has_previous():
		page_obj_prev = page_obj.previous_page_number()
	else:
		page_obj_prev = 1
	
	total_pages = paginator.num_pages
	links = {'next': page_obj_next, 'prev':page_obj_prev}

	# Here I map a lambda function over the queryset of Models to 
	# return the dictionary representation for each element in the list
   
	quotes = list(map(lambda quote: quote.serialize(), list(page_obj)))
	return JsonResponse({
		"quotes":quotes,
		"links":{
			'next': page_obj_next,
			'prev': page_obj_prev,
			'total_pages': total_pages
			}
		})
	
	# return JsonResponse([quote.serialize() for quote in quotes], safe=False)
@csrf_exempt
def search(request):
	query = request.GET.get('q', '')
	print(query)
	quotes= Quote.objects.filter(quote__icontains=query) | Quote.objects.filter(song__icontains=query) | Quote.objects.filter(artist__icontains=query)
	print(quotes)
	if len(quotes)>0:
		# handle empty querySet here return not found error
		# quotes = Quote.objects.all().order_by("-timestamp")
		page_num = request.GET.get('page')
		paginator = Paginator(quotes, 3)
		try:
			page_obj= paginator.get_page(page_num)

		except PageNotAnInteger:
			page_obj= {'error', 'Invalid Page'}

		except EmptyPage:
			page_obj = paginator.get_page(1)


		if page_obj.has_next():
			page_obj_next = page_obj.next_page_number()
		else:
			page_obj_next = 1

		if page_obj.has_previous():
			page_obj_prev = page_obj.previous_page_number()
		else:
			page_obj_prev = 1
		
		total_pages = paginator.num_pages
		links = {'next': page_obj_next, 'prev':page_obj_prev}

		# Here I map a lambda function over the queryset of Models to 
		# return the dictionary representation for each element in the list
	   
		quotes = list(map(lambda quote: quote.serialize(), list(page_obj)))
		print(quotes)
		return JsonResponse({
			"quotes":quotes,
			"links":{
				'next': page_obj_next,
				'prev': page_obj_prev,
				'total_pages': total_pages
				}
			}, status=200)
		
	# elif len(response_lst)>0 and request.method=='GET':
	# 	return JsonResponse(response_lst[0])
	else :
		return JsonResponse({"NotFound": "Search query yield no response"}, status=404)


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

@csrf_exempt
def submitQuote(request):
	if request.user.is_authenticated:
		if request.method=='POST':
			form = request.POST
			print(form['quote'])
			# if form.is_valid():
			quote = form['quote']
			artist = form['artist']
			song = form['source']
			image = form['image']
			contributor=User.objects.get(id=request.user.id)
			quote = Quote(quote=quote, artist=artist, song=song, image=image, contributor=contributor)
			quote.save()
			return render(request, "afroquotes/index.html")
		else:
			return JsonResponse({"message": "Not Allowed"}, status=400)
	else:

		return render(request, "afroquotes/login.html")


def annotate(request, quote_id):

	# query for requested qoute
	try:
		quote = Quote.objects.get(id=quote_id)
		quote=quote.serialize()
	except Quote.DoesNotExist:
		return JsonResponse({"error": "quote not found"}, status=404)
	if request.method == "GET":
		try:
			quoteAnnotQuery = Annotation.objects.get(annotated=quote_id)
			print(quoteAnnotQuery.serialize())
			quoteAnnotQuery.last_viewed=datetime.now()
			quoteAnnotQuery.annotation_view_count+=1
			quoteAnnotQuery.save()
			if request.user.is_authenticated:
				user=request.user
				print(f"Looookkk::::: a {user.id}")
				upvoted = quoteAnnotQuery.get_user_upvote(user.id)
				_annotation=quoteAnnotQuery.serialize()
				_annotation["upvoted"]=upvoted
				print(_annotation)
				# return JsonResponse(_annotation, status=200)
				return JsonResponse({"quote": quote, "annotation": _annotation }, status=200)
			else:
				_annotation=quoteAnnotQuery.serialize()
				_annotation["upvoted"]='none'
				# return JsonResponse(_annotation, status=200)
				return JsonResponse({"quote": quote, "annotation": _annotation }, status=200)
			# print(quoteAnnotQuery)
		except Annotation.DoesNotExist :
			print (Annotation.DoesNotExist)
			quote = Quote.objects.get(id=quote_id)
			quote = quote.serialize()
			response = {"quote": quote, "annotation": "None" }
			print(response)

			return JsonResponse({"quote": quote, "annotation": "None" }, status=200)
			# returning error to fetch request from JS. This is deprecated. Now render without JSON
			# return JsonResponse({"Error": "There are no annotations for this Quote."}, status=404)
		return JsonResponse({"NotFound": "There are no annotations for this Quote."}, status=400)

		{"data":{"quote": quoteAnnotQuery.serialize(), "annotation": "None" }}

	   
@csrf_exempt
def submit_annotation(request, quote_id):
	quote_id = int(quote_id)
	annotated = Quote.objects.get(id=quote_id)

	if request.method=='POST':
		if request.user.is_authenticated:
			form = json.loads(request.body)
			print(form)
			
			annotation = form['annotation'].strip()
			if annotation:
				print(annotation)
				annotator= request.user
				annotation = Annotation(annotation=annotation, annotator=annotator, annotated=annotated)
				annotation.save()

				# return render(request, "afroquotes/annotation.html",{
				# 	"form":Annotate(),
				# 	"quote": annotated,
				# 	"annotations": Annotation.objects.filter(annotated=annotated)
				# 	})
				annotation = annotation.serialize()
				annotated=annotated.serialize()
				annotation["upvoted"]='none'
				return JsonResponse({'annotation':annotation, 'quote':annotated}, status=200)

		else:
			print("Unauthorized user not allowed!")
			return JsonResponse({"AuthenticationError": "you need to login first!"}, status=404)
			
	else:
		return JsonResponse({"message": "not allowed"}, status=400)
		

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
		user = request.user
		# annoid = data.get("annotation")
		annotation = Annotation.objects.get(id=annoid)
		pre_upvoted = Upvote.objects.filter(user=user, annotation=annotation)
		if not pre_upvoted:
			upvote = Upvote(annotation=annotation, user=user)
			upvote.save()
		else:
			upvote = Upvote.objects.filter(annotation=annotation, user=user)
			upvote[0].delete()
			upvote = Upvote.objects.filter(annotation=annotation, user=user)

		
		annotation = Annotation.objects.get(id=annoid)
		upvoted = annotation.get_user_upvote(user.id)
		annotation=annotation.serialize()
		annotation["upvoted"]=upvoted


		
				

			# return HttpResponseRedirect(reverse("annotate", args=(annotation.annotated.id,)))
		return JsonResponse(annotation, status=200)
	else:
		return JsonResponse({"Login": "Login required to perform this action!"}, status=400)


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

		










