from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(AbstractUser):

    username = models.CharField(
        _('username'),
        max_length=100,
        help_text=_('Username, 100 characters or fewer.'),
        error_messages={
            'unique': _('Username already taken.')
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email'), unique=True, error_messages={
        'unique': _('A user with this email address already exists.')
    })
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'),)
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    login_count = models.IntegerField(editable=False, default=0)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def friends_by_requests_sent(self):
        friend_requests = self.friend_requests_sent.filter(is_accepted=True, is_cancelled=False)
        friend_users = []
        for friend_request in friend_requests:
            friend_users.append(friend_request.receiver)
        return friend_users

    def friends_by_requests_received(self):
        friend_requests = self.friend_requests_received.filter(is_accepted=True, is_cancelled=False)
        friend_users = []
        for friend_request in friend_requests:
            friend_users.append(friend_request.sender)
        return friend_users

    def active_friend_requests_exist(self):
        sent_exist = self.friend_requests_sent.filter(sender=self, is_accepted=False, is_cancelled=False).exists()
        received_exist = self.friend_requests_received.filter(receiver=self, is_accepted=False, is_cancelled=False).exists()
        return sent_exist or received_exist

    def friends(self):
        return self.friends_by_requests_sent() + self.friends_by_requests_received()

    def friends_queryset(self):
        query = Q(sender=self) | Q(receiver=self)
        return FriendRequest.objects.filter(query)



class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_received")
    is_accepted = models.BooleanField(default=False, help_text=_('designates whether this friend request is accepted '
                                                                 'or rejected by receiver'))
    is_cancelled = models.BooleanField(default=False, help_text=_('designates whether this friend request is '
                                                                  'cancelled by sender before being accepted'))
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)


    def clean(self):
        inserting = False if self.pk else True
        if self.sender == self.receiver:
            raise ValidationError("Sender and receiver cannot be the same user.")

        if inserting and FriendRequest.objects.filter(sender=self.sender, receiver=self.receiver).exists():
            raise ValidationError("A friend request between these users already exists.")

        if inserting and FriendRequest.objects.filter(sender=self.receiver, receiver=self.sender).exists():
            raise ValidationError("A friend request between these users already exists.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                name='unique_friend_request'
            ),
            models.UniqueConstraint(
                fields=['receiver', 'sender'],
                name='unique_friend_request_reverse'
            )
        ]
