from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Post, CustomUser, Comment
# from taggit.models import Tag


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        "username",
        "email",
        "last_login",
        "is_staff",
        "is_active",
    ]
    ordering = ("email",)
    search_fields = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
# admin.site.register()
