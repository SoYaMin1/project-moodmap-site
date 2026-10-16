from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


def avatar_upload_to(instance, filename):
    """Путь: avatars/<user_id>/<uuid>.<ext>"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"avatars/{instance.user_id}/{uuid.uuid4().hex}.{ext}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField("Телефон", max_length=32, blank=True)
    bio = models.CharField("О себе", max_length=160, blank=True)
    avatar = models.ImageField(
        "Аватар",
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        help_text="PNG, JPG или WEBP, до 2 МБ",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return None


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()