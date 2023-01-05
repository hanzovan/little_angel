from django.urls import path
from . import views

app_name = "kids"

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register', views.register, name="register"),
    path('add_course', views.add_course, name="add_course"),
    path('add_kid', views.add_kid, name="add_kid"),
    path('kids', views.kids, name="kids"),
    path('kids/<int:kid_id>', views.kid_detail, name="kid_detail"),
    path('kids/evaluate', views.aspect_evaluate, name="evaluate"),
    path('kids/evaluation', views.evaluation, name="evaluation"),
    path('courses/<int:course_id>', views.course_detail, name="course_detail"),
    path('course/register', views.course_register, name="course_register"),
    path('course/quit_course', views.quit_course, name="quit_course"),
    path('refresh_duration', views.refresh_duration, name="refresh_duration"),
    path('spend_time', views.spend_time, name="spend_time")
]