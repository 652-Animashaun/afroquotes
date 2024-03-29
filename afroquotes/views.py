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
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views import View
from rest_framework.authtoken.models import Token
from djrichtextfield.widgets import RichTextWidget
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from rest_framework import status
from .youtube_charts import search_youtube
# from mongo_utils import get_db_handle
from bson.objectid import ObjectId
from .models import *
# from .nonrel_model import *
from . import config
from .serializers import *
import logging



# Create your views here.
class SubmitQuoteForm(forms.Form):
    quote = forms.CharField(widget=forms.Textarea())
    song = forms.CharField(max_length=64)
    artist= forms.CharField(max_length=64)
    image = forms.URLField()
    quote_id = forms.CharField(required=False)

class SubmitQuotePatch(forms.Form):
    quote_id = forms.IntegerField()

class AnnotateForm(forms.Form):
    annotation=forms.CharField(max_length=300)
class searchForm(forms.Form):
    queryTerm= forms.CharField(max_length=32)
class SuggestImprove(forms.Form):
    comment = forms.CharField(min_length=32, max_length=300)





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

class CreateUserAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logging.info(f"CreateUserAPIView, create user request: {request}")
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        logging.info(f"CreateUserAPIView CreateRequest for user {request.data}")
        try:
            user = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
           
            logging.info(user)
            return Response(
                    {**serializer.data}
                )
        
        except ValueError as ex:
            logging.error(f"CreateUserAPIView ValueError: {ex} ")
            # logger.warning(f"CreateUserAPIView ValueError: {ex} ")
            print(f"CreateUserAPIView serializers.ValidationError: {ex} ")
            return JsonResponse({"error":str(ex)})
            
        except serializers.ValidationError as err:
            logging.error(f"CreateUserAPIView serializers.ValidationError: {err} ")
            # logger.warning(f"CreateUserAPIView serializers.ValidationError: {err} ")
            print(f"CreateUserAPIView serializers.ValidationError: {err} ")
            
            return JsonResponse({"error":str(err)})
        except Exception as ex:
            print(f"PRINT    CreateUserAPIView serializers.ValidationError ")
            logging.exception(f"CreateUserAPIView Exception: {ex} ")


class UserAuth(ObtainAuthToken):
    """
    Serves request to authenticate a app user 
    sub-classing the ObtainAuthtoken rest-framework auth class
    """
    # serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            logging.info(f"UserAuth Login request for user {user.email}")
            logging.info(f"UserAuth Login request for user {user.email}")
            
            token, created = Token.objects.get_or_create(user=user)
            user = UserSerializer(user)
            return Response({
                'token': token.key,
                'user': user.data
            })
        except ValidationError as err:
            logging.info(f"UserAuthr: {err} ")
            logging.error("UserAuth Error")
            return Response({"Error":str(err)})
        except Exception as ex:
            return JsonResponse({"Error": str(ex)}, safe=False, status=400)

class AllQuotes(APIView):
    def get(self, request):
        quotes = get_all_quotes()
        quotes = Quote.objects.all().order_by("-timestamp")
        page_num = request.GET.get('page')

        paginator = Paginator(quotes, 10)
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
        quotes = list(map(lambda quote: quote.serialize(), list(page_obj)))

        
        return Response({"quotes":quotes, "total_pages":total_pages})

    
# @csrf_exempt
@api_view(["GET","POST"])
def search(request):
    query = request.GET.get('q', '')
    print(query)
    quotes= Quote.objects.filter(quote__icontains=query) | Quote.objects.filter(song__icontains=query) | Quote.objects.filter(artist__icontains=query)
    print(quotes)
    if len(quotes)>0:
        # handle empty querySet here return not found error
        # quotes = Quote.objects.all().order_by("-timestamp")
        page_num = request.GET.get('page')
        paginator = Paginator(quotes, 5)
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
    
        return Response({"quotes":quotes, "total_pages":total_pages})
        
    else :
        return Response({"message":"No Results"})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))




class SubmitQuoteClass(APIView):
    # form = SubmitQuoteForm
    serializer_class = QuotesSerializer
    # initial = {'key': 'value'}
    template_name = 'afroquotes/submit_quote.html'


    def post(self, request):
        logging.info(f"user Request from user: {request.user} ")
        print(f"user Request from user: {request.user} ")
        contributor=request.user
        contributed_quotes = Quote.objects.filter(contributor=contributor)
        annotation_iq = request.user.get_annotation_iq()
        unverified_annotations = Annotation.objects.filter(verified=False).exclude(annotator=contributor, approvers=contributor)
        data = request.data.copy()
        data['contributor']=contributor.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        contributed_quotes = Quote.objects.filter(contributor=contributor)
        return Response({"annotation_iq":annotation_iq, 'contributed_quotes': contributed_quotes, "unverified_annotations":unverified_annotations})



def view_annotation_page(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    annotation = Annotation.objects.filter(annotated=quote_id)
    if len(annotation)>0:
        annotation = annotation[1]
    else:
        annotation = None
    context = {"quote":quote, "annotation":annotation}
    return render(request, "afroquotes/annotations_page.html", context )



       
@csrf_exempt
def submit_annotation(request, quote_id):
    if request.method=='POST':
        
        if request.user.is_authenticated:

            form = AnnotateForm(request.POST)
            if form.is_valid():
                annotation = form.cleaned_data['annotation']
                quote_id = int(quote_id)
                annotated = Quote.objects.get(id=quote_id)
                # contributor = User.objects.get(id=request.user.id)
                annotator= request.user
                annotation = Annotation(annotation=annotation, annotator=annotator, annotated=annotated)
                annotation.save()
                annotation = annotation.serialize()
            quotes = get_all_quotes()
            quotes["form"] = form

                
            return HttpResponseRedirect("index")

        else:
            print("Unauthorized user not allowed!")
            return HttpResponseRedirect(reverse("login"))
            
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

# @csrf_exempt
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
        return JsonResponse({"Unauthorized": "Login required to perform this action!"}, status=401)
        # return HttpResponseRedirect(reverse("login"))


@csrf_exempt
def submit_suggestion(request, annoID):
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
                # return render(request, "afroquotes/index.html", quotes)
                return JsonResponse({"suggested":suggestioncomm.serialize()}, status=201)

            except Annotation.DoesNotExist:
                return JsonResponse({"Error": "not found" }, status=500)
        else:
            return JsonResponse({"Error":"method not allowed"}, status=400)
    else:
        return JsonResponse({"Unauthorized":"Login required to perform this action!"}, status=401)

        
def get_all_quotes():

    quotes = Quote.objects.all().order_by("-timestamp")

    quote_list=[]
    quotes_dict = {"quotes":quote_list}

    for q in quotes:
        annotation = Annotation.objects.filter(annotated=q)

        if len(annotation) > 0:
            annotation = annotation[0].serialize()
            quote={"quote":q, "annotation":annotation}
        else:
            quote={"quote":q, "annotation":None}
        quote_list.append(quote)
        # print(quote.get("annotation"))
    list_quote = quotes_dict.get("quotes")  
    quotes = quotes_dict
    return quotes

def quote_chart(request, slug):

    if slug=="top100":
        annotations = Annotation.objects.all().order_by('-annotation_view_count')[:100]

    else:
        annotations = Annotation.objects.all().order_by('-annotation_view_count')[:11]
        slug = "top10"

    serialed_annotations=[]

    for annotation in annotations:
        annotation = annotation.serialize()
        serialed_annotations.append(annotation)

    return render(request, "afroquotes/charts.html", {"annotations":serialed_annotations, "slug":slug})

    

def view_on_yt(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    video_id = search_youtube(quote.song)
    link = f"https://www.youtube.com/watch?v={video_id}"
    return HttpResponseRedirect(link)
    # return JsonResponse({"link":link}, 200)




