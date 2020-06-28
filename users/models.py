from django.contrib.auth.models import AbstractUser
from django.db import models

PRIMARY_ACTIVITIES = (
    (0, 'Buyer'),
    (1, 'Seller'),
    (2, 'Agent'),
)


class Company(models.Model):
    server_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    primary_activity = models.PositiveSmallIntegerField(
        choices=PRIMARY_ACTIVITIES,
        help_text="Used to redirect logged-in user to the appropriate admin site.",
        default=0)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class User(AbstractUser):
    server_id = models.IntegerField(unique=True, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=False)
