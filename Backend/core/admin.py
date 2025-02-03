from django.contrib import admin
from django import forms

from core.models import UserProfile, UserFile


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_name', 'get_email', 'is_editor', 'get_is_staff')
    search_fields = ('user__name', 'user__email')
    list_select_related = ['user']
    list_display_links = ["get_username"]
    form = UserAdminForm

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_is_staff(self, obj):
        return obj.user.is_staff
    get_is_staff.short_description = 'Is Staff'


class UserFileAdminForm(forms.ModelForm):
    class Meta:
        model = UserFile
        exclude = ()


@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'source', 'user')
    search_fields = ('user__name', 'user__email')
    list_select_related = ['user']

