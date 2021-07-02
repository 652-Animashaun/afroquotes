from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("submitQuote", views.submitQuote, name="submitQuote"),
    path("annotation/<int:quote_id>", views.annotate, name="annotate"),
    # path("<int:quote_id>", views.quote, name="quote"),
    path("annotate/<int:quote_id>", views.write_annotate, name="write_annotate"),
    path("quote_by/<str:filt_term>", views.quote_by, name="quote_by"),
    path("quote_from/<str:filt_term>", views.quote_from, name="quote_from"),
    path("upvote/<int:annoid>", views.upvote, name="upvote"),
    path("submitSugg/<int:annoID>", views.submitSuggestion, name="submitSuggestion")

]