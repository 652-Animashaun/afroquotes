from django.urls import path
from . import views

urlpatterns = [
    path("", views.AllQuotes.as_view(), name="index"),
    # path("quotes", views.get_all_quotes, name="quotes"),
    path("login", views.login_view, name="login"),
   
    path('register', views.register, name='register'),
    path("logout", views.logout_view, name="logout"),
    path("submitquote", views.SubmitQuoteClass.as_view(), name="submitQuote"),
    path("search", views.search, name="search"),
]