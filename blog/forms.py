from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from django import forms
from .models import Post, Comment
from taggit.forms import TagWidget

# create SignUp form
User = get_user_model()


# user registration form
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "form-control", "placeholder": field.label}
            )

        # custom labels
        self.fields["password2"].label = "Confirm Password"

        # custom placeholder (override defaults)
        self.fields["email"].widget.attrs["placeholder"] = "john.doe@email.com"
        self.fields["password1"].widget.attrs["placeholder"] = "Enter password"
        self.fields["password2"].widget.attrs["placeholder"] = "Re-enter password"


# password change form
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        # loop through all fields
        for _, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                }
            )

        # Customize labels + placeholders
        self.fields["old_password"].label = "Current Password"
        self.fields["old_password"].widget.attrs[
            "placeholder"
        ] = "Enter current password"

        self.fields["new_password1"].label = "New Password"
        self.fields["new_password1"].widget.attrs["placeholder"] = "Enter new password"

        self.fields["new_password2"].label = "Confirm New Password"
        self.fields["new_password2"].widget.attrs["placeholder"] = "Confirm password"


# Custom SetPasswordForm for password reset
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "form-control", "placeholder": field.label}
            )

        self.fields["new_password1"].label = "New Password"
        self.fields["new_password1"].widget.attrs[
            "placeholder"
        ] = "Enter new password (min 8 chars)"

        self.fields["new_password2"].label = "Confirm New Password"
        self.fields["new_password2"].widget.attrs[
            "placeholder"
        ] = "Confirm new password"


# form to edit your profile
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            # "email",
            "username",
        )
        widgets = {"username": forms.TextInput(attrs={"class": "form-control"})}

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if username:
            # normalize email
            username = username.strip().lower()

            # check if email already exists (excluding current user)
            if (
                User.objects.filter(username=username)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError("Username is already taken")

        return username


# post creation form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "tags")
        widgets = {
            "tags": TagWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tags"].required = False

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {"class": "form-control", "placeholder": field.label}
            )

    def clean_title(self):
        title = self.cleaned_data.get("title")

        if not title:
            raise forms.ValidationError("Title is required")

        # clean title
        # if title:
        title = title.strip()

        # check if title length of characters is less than 10
        if len(title) < 10:
            raise forms.ValidationError("Title of post cannot less than 10 characters")

        return title


# comment form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)

        widgets = {
            "content": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Write yout comment ..."}
            )
        }

    def clean_content(self):
        content = self.cleaned_data.get("content")
        content = content.strip()
        # check if not content (comment is provided)
        if not content:
            raise forms.ValidationError("Comment content must be provided")

        return content
