from django.contrib.auth import logout
from django.db.models import Q
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
from .throttler import FriendRequestThrottle
from .serializers import UserSerializer
from .serializers import FriendRequestSerializer
from .serializers import UserLoginSerializer
from .serializers import UserLogoutSerializer


class SignUpAPIView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request):
        context = {
            'request': request
        }
        serializer = UserSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        context = {
            'request': request,
        }
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        serializer = UserSerializer(user, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    serializer_class = UserLogoutSerializer
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'User logged out'}, status=status.HTTP_204_NO_CONTENT)

class APIBaseView(APIView):
    def get(self, request, format=None):
        kwargs = {
            'pk': request.user.id,
        }
        if request.user.is_authenticated:
            data = {
                'logout': reverse('logout', request=request, format=format),
                'users': reverse('user-list', request=request, format=format),
                'friends': reverse('friend-list', kwargs=kwargs, request=request, format=format),
                'friend requests': reverse('friend-create', request=request, format=format),
            }
        else:
            data = {
                'login': reverse('login', request=request, format=format),
                'register': reverse('register', request=request, format=format),
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
            email_exacting_users = users.filter(email__iexact=search_query)
            if email_exacting_users.exists():
                users = email_exacting_users
            else:
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

    def get(self, request, *args, **kwargs):
        friends = request.user.friends()
        context = {
            'request': request,
        }
        serializer = UserSerializer(friends, context=context, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSerializer
    queryset = FriendRequest.objects.all().order_by('-created_on')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        print(self.request.method)
        if self.request.method in ['GET', 'PUT', 'PATCH']:
            context['read_only_fields'] = []
        else:
            context['read_only_fields'] = ['is_accepted', 'is_cancelled']
        return context

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        if self.request.method in ['PUT', 'PATCH']:
            kwargs['partial'] = True
        return FriendRequestSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        friend_request = FriendRequest.objects.get(id=kwargs.get('pk'))
        context = {
            'request': request,
        }
        serializer = FriendRequestSerializer(friend_request, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        is_accepted = serializer.validated_data.get('is_accepted')
        is_cancelled = serializer.validated_data.get('is_cancelled')

        instance.is_accepted = is_accepted
        instance.is_cancelled = is_cancelled
        instance.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendRequestAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FriendRequest.objects.all().order_by('-created_on')
    serializer_class = FriendRequestSerializer
    throttle_classes = [FriendRequestThrottle]

    def get(self, request, *args, **kwargs):
        # http://localhost:8000/api/users/friends/?state=accepted
        state_query = request.query_params.get('state', '').strip().lower()
        query = Q(sender=request.user) | Q(receiver=request.user)
        if state_query == 'pending':
            friend_requests = FriendRequest.objects.filter(query, is_accepted=False)
        elif state_query == 'accepted':
            friend_requests = FriendRequest.objects.filter(query, is_accepted=True)
        else:
            friend_requests = FriendRequest.objects.filter(query)
        print(query)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(friend_requests, request)
        context = {
            'request': request,
        }
        serializer = FriendRequestSerializer(page, context=context, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        context = {
            'request': request
        }
        serializer = FriendRequestSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save(sender=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





