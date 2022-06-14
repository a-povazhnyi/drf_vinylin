from django.contrib import admin

from .models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'is_email_verified')
    list_display_links = ('id', 'email', 'full_name')

    @staticmethod
    def full_name(obj):
        return f'{obj.first_name} {obj.last_name}'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'age', 'country')
    list_display_links = ('id', 'user')
    save_on_top = True
