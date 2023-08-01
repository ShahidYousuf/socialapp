from rest_framework import serializers
from .models import User
from .models import FriendRequest
from django.contrib.auth import authenticate
from django.contrib.auth import login


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.username = user.email
        user.set_password(password)
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def partial_update(self, instance, validated_data):
        return self.update(instance, validated_data)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        request = self.context['request']

        user = authenticate(request, username=email, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError('Incorrect credentials. Please try again.')
        login(request, user)
        data['user'] = user
        return data

class UserLogoutSerializer(serializers.Serializer):
    pass

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(method_name='get_sender')

    def get_sender(self, obj):
        return obj.sender.id

    class Meta:
        model = FriendRequest
        fields = ['url', 'sender', 'receiver', 'is_cancelled', 'is_accepted']
        extra_kwargs = {
            'sender': {'read_only': True},  # Set 'sender' field as read-only
        }

    def validate(self, data):
        sender = self.context['request'].user
        receiver = data['receiver']

        # Validate that sender and receiver are different users
        put_or_patch = True if self.context['request'].method in ['PATCH', 'PUT'] else False
        if not put_or_patch and sender == receiver:
            raise serializers.ValidationError("Sender and receiver cannot be the same user.")

        # Enforce bidirectional uniqueness for friend requests
        if not put_or_patch:
            sender_friend_request_exists = FriendRequest.objects.filter(sender=sender, receiver=receiver).exists()
            receiver_friend_request_exists = FriendRequest.objects.filter(sender=receiver, receiver=sender).exists()
            if sender_friend_request_exists or receiver_friend_request_exists:
                raise serializers.ValidationError("A friend request between these users already exists.")
        # Ensure a user cannot send a friend request to themselves
        if FriendRequest.objects.filter(sender=sender, receiver=sender).exists():
            raise serializers.ValidationError("A user cannot send a friend request to themselves.")

        # Ensure is_accepted and is_cancelled fields are not set to True simultaneously
        is_accepted = data.get('is_accepted')
        is_cancelled = data.get('is_cancelled')
        if is_accepted and is_cancelled:
            raise serializers.ValidationError("A friend request cannot be both accepted and cancelled.")

        return data
