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
    path('kids/kid_evaluate', views.kid_evaluate, name="kid_evaluate"),
    path('kids/evaluate', views.aspect_evaluate, name="evaluate")
]