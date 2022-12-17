from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# Create your models here.
class User(AbstractUser):
    account = models.PositiveIntegerField(default=0)


class Kid(models.Model):
    nickname = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    birthday = models.DateField()
    parent = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='creators')
    
    # Time available per month by hours
    time = models.IntegerField(default=672)
    
    class Gender(models.TextChoices):
        FEMALE = 'FE', 'Female'
        MALE = 'MA', 'Male'
    gender = models.CharField(
        max_length=2,
        choices=Gender.choices
    )

    class Status(models.IntegerChoices):
        VERY_LOW = 1
        LOW = 2
        NORMAL = 3
        GOOD = 4
        EXCELLENT = 5
    status = models.IntegerField(choices=Status.choices)

    physical_growth = models.IntegerField(choices=Status.choices, default=3)
    motor = models.IntegerField(choices=Status.choices, default=3)
    cog_int = models.IntegerField(choices=Status.choices, default=3)
    social_emotional = models.IntegerField(choices=Status.choices, default=3)
    language_communication = models.IntegerField(choices=Status.choices, default=3)
    gender_growth = models.IntegerField(choices=Status.choices, default=3)
    race = models.IntegerField(choices=Status.choices, default=3)

    def __str__(self):
        return f"{self.nickname} who is currenly in {self.status} potential"


# Aspects of kid's development
class Aspect(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.title}"


# Courses
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    category = models.CharField(max_length=255, blank=True)    
    img_URL = models.URLField(blank=True)
    goal = models.ManyToManyField(Aspect, blank=True, related_name="target")
    
    # cost per 4 weeks
    cost = models.IntegerField(default=0)
    starting_date = models.DateField(blank=True)
    
    # Time require per 4 weeks by hours
    time_cost = models.IntegerField()

    student = models.ManyToManyField(Kid, blank=True, related_name="learner")

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


# Evaluation from aspects
class Evaluation(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)    
    kid = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="kid_evaluation")
    aspect = models.ForeignKey(Aspect, on_delete=models.CASCADE, related_name="aspect_evaluation")
    
    # Point from 1 to 5
    qualified = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True)

    def __str__(self):
        return f"{self.title} for {self.kid} in {self.aspect}: {self.qualified}"


# Expectation of kids from courses
class Expectation(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    kid = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="kid_expectation")
    aspect = models.ForeignKey(Aspect, on_delete=models.CASCADE, related_name="aspect_expectation")

    # Point from 1 to 5
    qualified = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True)