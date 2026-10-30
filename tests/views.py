"""Views and viewsets shared by the tests."""

from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirectBase
from rest_framework import generics, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_query_method import filters, viewsets


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class QueryEchoView(APIView):
    permission_classes = []
    authentication_classes = []

    def query(self, request):
        return Response({"method": request.method, "data": request.data})


class TemporaryRedirect(HttpResponseRedirectBase):
    status_code = 307


@api_view(["QUERY"])
def redirect_view(request):
    return TemporaryRedirect("/query/")


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username"]
    ordering_fields = ["username"]
    ordering = ["-username"]

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PlainUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []


class QueryActionViewSet(viewsets.GenericViewSet):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []

    def list(self, request):
        return Response("list")

    @action(detail=False, methods=["post"])
    def query(self, request):
        return Response("action")


class SessionQueryView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def query(self, request):
        return Response({"method": request.method})

    def post(self, request):
        return Response({"method": request.method})
