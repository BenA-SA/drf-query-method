from django.urls import path

from tests.views import QueryEchoView, redirect_view

urlpatterns = [
    path("query/", QueryEchoView.as_view()),
    path("redirect/", redirect_view),
]
