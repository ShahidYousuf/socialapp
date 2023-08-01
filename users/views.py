from django.views import View
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.reverse import reverse
from .models import User
from .models import FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer

# Create your views here.
class SignUpView(View):
    ...

class LoginView(View):
    form_class = AuthenticationForm

    def post(self, request, *args, **kwargs):
        post_data = request.POST.copy()
        next_url = post_data.get('next', '/')
        email = post_data.get('email', None)
        password = post_data.get('password', None)
        if email and password:
            email = str(email).strip().lower()
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(to=next_url)

class APIBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        kwargs = {
            'pk': request.user.id,
        }
        data = {
            'users': reverse('user-list', request=request, format=format),
            'friends': reverse('friend-list', kwargs=kwargs, request=request, format=format)
        }
        return Response(data, status=status.HTTP_200_OK)

class UserListAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    pagination_class = PageNumberPagination
    display_edit_forms = True
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        # http://127.0.0.1:8000/api/users/?search=shahid&page_size=5
        users = User.objects.all().exclude(id=request.user.id).order_by('-created_on')

        search_query = request.query_params.get('search', '').strip().lower()
        page_size = request.query_params.get('page_size', 10)
        if search_query:
            db_search_query = Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
            users = users.filter(db_search_query)

        paginator = self.pagination_class()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(users, request)
        context = {
            'request': request,
            'display_edit_forms': True
        }
        serializer = UserSerializer(page, context=context, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = {
            'request': request
        }
        serializer = UserSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.get('pk'))
        context = {
            'request': request,
        }
        serializer = UserSerializer(user, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendListAPIView(APIView):
    login_url = '/users/login/'
    redirect_field_name = 'next'
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        friends = request.user.friends()
        context = {
            'request': request,
        }
        serializer = UserSerializer(friends, context=context, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



