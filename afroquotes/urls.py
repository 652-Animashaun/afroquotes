from django.urls import path
from . import views

urlpatterns = [
    path("", views.AllQuotes.as_view(), name="index"),
    path("upvote", views.upvote, name="upvote"),
    path("auth/login", views.UserAuth.as_view(), name="login"),
   
    path('auth/register', views.CreateUserAPIView.as_view(), name='register'),
    path("logout", views.logout_view, name="logout"),
    path("submitquote", views.SubmitQuoteClass.as_view(), name="submitQuote"),
    path("search", views.search, name="search"),
    path("user", views.UserProfile.as_view(), name="view_user_profile"),
    path("user/editbio", views.UserProfile.as_view(), name="editbio"),
]