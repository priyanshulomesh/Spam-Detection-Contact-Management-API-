from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class Contact(models.Model):
    number = models.IntegerField(unique=True)
    reported_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="ReportDetails", related_name="flagged_contacts"
    )

    def __str__(self):
        return f"{self.number}"

class User(AbstractUser):
    full_name = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=25,unique=True, blank=True, null=True)
    primary_contact = models.OneToOneField(
        "Contact", on_delete=models.CASCADE, null=False, blank=False
    )

     # Explicitly define related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.full_name or self.username

class UserPhoneContact(models.Model):
    app_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50, null=True)

    class Meta:
        unique_together = ["app_user", "phone_contact"]

    def __str__(self):
        return f"{self.app_user.full_name} - {self.phone_contact.number}"


class ReportDetails(models.Model):
    phone_contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["reporter", "phone_contact"]

    def __str__(self):
        return f"{self.reporter.full_name} - {self.phone_contact.number}"
