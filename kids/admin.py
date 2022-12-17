from django.contrib import admin
from .models import User, Kid, Aspect, Course, Evaluation, Expectation

# Register your models here.
admin.site.register(User)

admin.site.register(Kid)
admin.site.register(Aspect)
admin.site.register(Course)
admin.site.register(Evaluation)
admin.site.register(Expectation)