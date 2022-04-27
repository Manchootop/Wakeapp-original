from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()


class Event(models.Model):

    PERSONAL = "Приятелски"
    SPORT = "спортен"
    CULTURAL = "културен"
    CIVIL = "граждански"
    COMMERCIAL = "комерсиален"
    POLITICAL = "политически"

    TYPES = [(x, x) for x in (PERSONAL, SPORT, CULTURAL, CIVIL, COMMERCIAL, POLITICAL)]

    title = models.CharField(
        max_length=100,
    )
    type = models.CharField(
        max_length=max(len(x) for (x, _) in TYPES),
        choices=TYPES,
    )

    def __str__(self):
        return self.title

    description = models.TextField(
        max_length=255,
    )

    recommendations = models.TextField(
        max_length=255,
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=50,
    )

    publication_date = models.DateTimeField(
        auto_now_add=True,
    )

    likes = models.IntegerField(
        default=0,
    )

    views = models.IntegerField(
        default=0,
    )

    is_displayed = models.BooleanField(
        default=True,
    )

    organizer = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='organizer',
    )

    invited_users = models.ManyToManyField(
        UserModel,
        related_name='invited_users',
    )


    class Meta:
        unique_together = ('organizer', 'title')
