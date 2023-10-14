from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("quotes", views.get_all_quotes, name="quotes"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("submitquote", views.SubmitQuoteClass.as_view(), name="submitQuote"),
    path("annotation/<int:quote_id>", views.view_annotation_page, name="annotate"),
    # path("<int:quote_id>", views.quote, name="quote"),
    path("submit_annotation/<int:quote_id>", views.submit_annotation, name="submit_annotation"),
    path("get_annotation/<int:quote_id>", views.get_annotation, name="annotate_update_view"),
    path("search", views.search, name="search"),
    path("quote_by/<str:filt_term>", views.quote_by, name="quote_by"),
    path("quote_from/<str:filt_term>", views.quote_from, name="quote_from"),
    path("upvote/<int:annoid>", views.upvote, name="upvote"),
    path("submit_suggestion/<int:annoID>", views.submit_suggestion, name="submit_suggestion"),
    path("charts/<str:slug>", views.quote_chart, name="quote_chart"),
    path("approve_annotation/<int:annotation_id>", views.approve_annotation, name="approve_annotation"),
    path("view_on_yt/<int:quote_id>", views.view_on_yt, name="view_on_yt"),

]