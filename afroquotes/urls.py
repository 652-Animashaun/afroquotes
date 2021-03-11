from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("submitQuote", views.submitQuote, name="submitQuote"),
    path("annotation/<int:quote_id>", views.annotate, name="annotate"),
    path("search-results/<str:query>", views.search, name="search")
]