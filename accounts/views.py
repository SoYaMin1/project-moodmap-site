from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect

from .forms import ProfileForm, StyledPasswordChangeForm


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("diary:dashboard")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,          # 👈 ОБЯЗАТЕЛЬНО
            instance=profile,
            user=request.user,
        )
        if form.is_valid():
            # Обработка "удалить текущий аватар"
            if request.POST.get("avatar-clear") and profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("accounts:profile_edit")
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def password_change(request):
    if request.method == "POST":
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль изменён")
            return redirect("accounts:profile_edit")
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, "accounts/password_change.html", {"form": form})