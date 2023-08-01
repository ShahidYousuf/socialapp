from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import FriendRequest
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'login_count', 'is_active', 'is_staff')
    list_display_links = ('username', 'email',)
    actions= ['send_newsletter_issue']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name()

    # @admin.action(description='Send Newsletter Issue to Subscribers')
    # def send_newsletter_issue(self, request, queryset):
    #     subscribers = queryset.filter(is_active=True, groups__name__in=['Subscriber'])
    #     send_mass_newsletter_issue(subscribers)
    #     self.message_user(request, 'Newsletter issue was sent successfully! ', messages.SUCCESS)
    #
    # def send_subscription_activation_email(self, obj):
    #     link = reverse('subscription_activation', kwargs={'id': obj.id})
    #     if obj.is_active:
    #         return format_html(f"<button class='button' disabled style='background-color:darkgreen; color:white;'>Activated</button>")
    #     return format_html(f"<a href={link} class='button'>Send Activation Link</a>")



class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_accepted', 'is_cancelled',)
    list_display_links = ('sender', 'receiver',)



admin.site.register(User, CustomUserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)