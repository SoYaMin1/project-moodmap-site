from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile

INPUT_CLASS = "w-full px-3 py-2 rounded-md bg-white border border-slate-200 text-sm text-slate-900 outline-none focus:border-slate-900 transition"


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    username = forms.CharField(
        max_length=150, label="Никнейм",
        widget=forms.TextInput(attrs={"placeholder": "username"}),
    )

    class Meta:
        model = Profile
        fields = ("phone", "bio", "avatar")
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+7 999 000-00-00"}),
            "bio": forms.TextInput(attrs={"placeholder": "Пара слов о себе"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = self.user.email
        self.fields["username"].initial = self.user.username
        for name in ("username", "email", "phone", "bio"):
            self.fields[name].widget.attrs["class"] = INPUT_CLASS

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise forms.ValidationError("Этот никнейм уже занят.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar
        # если это уже существующий файл (например, поле не менялось)
        if not hasattr(avatar, "content_type"):
            return avatar
        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Файл больше 2 МБ.")
        if avatar.content_type not in (
            "image/jpeg", "image/png", "image/webp", "image/gif",
        ):
            raise forms.ValidationError("Только JPG, PNG, WEBP или GIF.")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.save()
        return profile


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs["class"] = INPUT_CLASS