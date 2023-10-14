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
from django.views import View
from djrichtextfield.widgets import RichTextWidget
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .youtube_charts import search_youtube

from .models import *


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




# def index(request):
#   return render(request, "afroquotes/index_js.html")
def index(request):
    # quotes = get_all_quotes()
    quotes = Quote.objects.all().order_by("-timestamp")
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
    quotes = list(map(lambda quote: quote.serialize(), list(page_obj)))

    
    return render(request, "afroquotes/index.html", {"quotes":quotes, "links":page_obj})


    
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
    
        return render(request, "afroquotes/index.html", {"quotes":quotes, "links":page_obj})
        
    else :
        return render(request, "afroquotes/index.html", {"message":"No Results"})


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

# @csrf_exempt
login_required()
def approve_annotation(request, annotation_id):
    annotation = Annotation.objects.get(id=annotation_id)
    if request.user.is_authenticated:
        if request.user not in [approver for approver in annotation.approvers.all()]:
            annotation.approvers.add(request.user)
            # annotation.save()
        annotation.check_veracity()
        return JsonResponse({"Message":"Approved"}, status=201)
    return JsonResponse({"Message":"Unauthorized"}, status=400)





class SubmitQuoteClass(View):
    form = SubmitQuoteForm
    # initial = {'key': 'value'}
    template_name = 'afroquotes/submit_quote.html'

    login_required()
    def get(self, request):
        if request.user.is_authenticated:
            contributor=User.objects.get(id=request.user.id)
            contributed_quotes = Quote.objects.filter(contributor=contributor)
            annotation_iq = request.user.get_annotation_iq()
            contributed_annotation = Annotation.objects.filter(annotator=request.user)
            unverified_annotations = Annotation.objects.filter(verified=False).exclude(annotator=contributor)
            unverified_annotations = unverified_annotations.exclude(approvers=contributor)

            print(len(unverified_annotations))
            # if there's a quote_id in the path params, then we only want to edit a quote
            if request.GET.get('quote_id'):
                quote_id = request.GET.get('quote_id')
                quote = Quote.objects.filter(id=quote_id).first()
                data = {
                'song': quote.song,
                'artist': quote.artist,
                'quote':quote.quote,
                'image':quote.image,
                'quote_id':quote.id,
                }

                form = self.form(initial=data)
                return render(request, self.template_name, {'form': form, "annotation_iq":annotation_iq, 'contributed_quotes': contributed_quotes, "unverified_annotations":unverified_annotations})
            return render(request, self.template_name, {'form': self.form, "annotation_iq":annotation_iq, 'contributed_quotes': contributed_quotes, "unverified_annotations":unverified_annotations})
        else:
            return render(request, "afroquotes/login.html")

    login_required()
    def post(self, request):
        if request.user.is_authenticated:
            contributor=User.objects.get(id=request.user.id)
            contributed_quotes = Quote.objects.filter(contributor=contributor)
            annotation_iq = request.user.get_annotation_iq()
            unverified_annotations = Annotation.objects.filter(verified=False).exclude(annotator=contributor, approvers=contributor)

            check_form = self.form(request.POST)
            if check_form.is_valid():
                if check_form.cleaned_data['quote_id']:
                    quote_id=check_form.cleaned_data['quote_id']
                # if request.POST.get('quote_id'):
                    quote = Quote.objects.filter(id=quote_id).first()
                    print(f"existing Quote: {quote.id}")
                    data = {
                    'song': quote.song,
                    'artist': quote.artist,
                    'quote':quote.quote,
                    'image':quote.image,
                    }
                    form = self.form(request.POST, initial=data)
                    print(form)
                    if form.has_changed():
                        for i in form.changed_data:
                            if i == 'quote':
                                quote.quote=form.cleaned_data['quote']
                            if i == 'artist':
                                quote.artist = form.cleaned_data['artist']
                            if i == 'song':
                                quote.song=form.cleaned_data['song']
                            if i == 'image':
                                quote.image= form.cleaned_data['image']
                                print(form.cleaned_data['image'])
                        quote.save()

                else:

                    form = self.form(request.POST)
                    if form.is_valid():
                        quote = form.cleaned_data['quote']
                        artist = form.cleaned_data['artist']
                        song = form.cleaned_data['song']
                        image = form.cleaned_data['image']
                        quote = Quote(quote=quote, artist=artist, song=song, image=image, contributor=contributor)
                        quote.save()
                contributed_quotes = Quote.objects.filter(contributor=contributor)
                return render(request, self.template_name, {'form': self.form, "annotation_iq":annotation_iq, 'contributed_quotes': contributed_quotes, "unverified_annotations":unverified_annotations})
            return render(request, self.template_name, {'form': check_form, "annotation_iq":annotation_iq, 'contributed_quotes': contributed_quotes, "unverified_annotations":unverified_annotations})
        return render(request, "afroquotes/login.html")

def get_annotation(request, quote_id):

    if request.method == "GET":
        try:
            quoteAnnotQuery = Annotation.objects.get(id=quote_id)
            quoteAnnotQuery.last_viewed=datetime.now()
            quoteAnnotQuery.annotation_view_count+=1
            quoteAnnotQuery.save()
            if request.user.is_authenticated:
                user=request.user
                upvoted = quoteAnnotQuery.get_user_upvote(user.id)
                _annotation=quoteAnnotQuery.serialize()
                _annotation["upvoted"]=upvoted
                # return JsonResponse(_annotation, status=200)
                return JsonResponse({"annotation": _annotation }, status=200)
            else:
                _annotation=quoteAnnotQuery.serialize()
                _annotation["upvoted"]='none'
                # return JsonResponse(_annotation, status=200)
                return JsonResponse({"annotation": _annotation }, status=200)
            # print(quoteAnnotQuery)
        except Annotation.DoesNotExist :
            raise 
            return JsonResponse({"quote": quote, "annotation": "None" }, status=200)
            # returning error to fetch request from JS. This is deprecated. Now render without JSON
            # return JsonResponse({"Error": "There are no annotations for this Quote."}, status=404)
        return JsonResponse({"NotFound": "There are no annotations for this Quote."}, status=400)

        # {"data":{"quote": quoteAnnotQuery.serialize(), "annotation": "None" }}

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




