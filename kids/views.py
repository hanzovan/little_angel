from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .helpers import strong_password, days_between
from datetime import datetime, timedelta, date

from django.contrib.auth import authenticate, login, logout

from .models import User, Kid, Course, Aspect, Evaluation, Expectation
from django.contrib.auth.decorators import login_required

# Import error handler
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def index(request):

    # if user logged in
    if request.user.is_authenticated:

        # If there is not request.session['message']
        if 'yay_message' not in request.session:
            request.session['yay_message'] = []

        yay_message = request.session['yay_message']

        # Clear message in request.session
        request.session['yay_message'] = ""

        if 'nay_message' not in request.session:
            request.session['nay_message'] = []

        nay_message = request.session['nay_message']

        request.session['nay_message'] = ""

        # test a case
        # i = Course.objects.get(id=1)
        # print(i.goal.all().values_list('title'))

        return render(request, "kids/index.html", {
            "courses": Course.objects.all(),
            "yay_message": yay_message,
            "nay_message": nay_message
        })

    # If user did not logged in
    else:
        return render(request, "kids/index.html", {
            "courses": Course.objects.all()
        })


# Allow user to login
def login_view(request):
    # If request method is post
    if request.method == "POST":

        # Get information from the form
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        # If authenticate success
        if user is not None:

            # Log the user in
            login(request, user)

            # Inform to the user and redirect to index
            request.session['yay_message'] = "Logged in successfully"
            return HttpResponseRedirect(reverse("kids:index"))
        
        # if authenticate fail
        else:
            return render(request, "kids/login.html", {
                "nay_message": "Invalid credentials"
            })        

    else:

        return render(request, "kids/login.html")


# Allow user to log out
def logout_view(request):
    logout(request)
    return render(request, "kids/login.html", {
        "yay_message": "Logged out successfully"
    })


# Allow user to create a new user
def register(request):
    # If form was submitted
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']
        email = request.POST['email']

        # check condition
        if not username:
            return render(request, "kids/register.html", {
                "nay_message": "Missing username"
            })

        if not password:
            return render(request, "kids/register.html", {
                "nay_message": "Missing password"
            })

        if not confirm:
            return render(request, "kids/register.html", {
                "nay_message": "You have to confirm password"
            })

        if not email:
            return render(request, "kids/register.html", {
                "nay_message": "Missing email"
            })

        if password != confirm:
            return render(request, "kids/register.html", {
                "nay_message": "Passwords don't match"
            })

        if not strong_password(password):
            return render(request, "kids/register.html", {
                "nay_message": "Password is not strong enough"
            })

        # If condition matched, try to add new user to database
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "kids/register.html", {
                "nay_message": "Username already taken"
            })

        login(request, user)
        request.session['yay_message'] = "Registered successfully"
        return HttpResponseRedirect(reverse("kids:index"))
            
    else:
        return render(request, "kids/register.html")

@login_required
def add_course(request):
    # If user submit form
    if request.method == "POST":
        # Define variables
        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']
        img_URL = request.POST['img_URL']
        benefits = request.POST.getlist('aspect')
        cost = request.POST['cost']
        starting_date = request.POST['starting_date']
        time_cost = request.POST['time_cost']
        aspects = []
        for benefit in benefits:
            i = Aspect.objects.get(title=benefit)
            aspects.append(i)

        # Check condition
        if not title or not description or not category or not img_URL or not cost or not time_cost or not starting_date:
            return render(request, "kids/add_course.html", {
                "nay_message": "All fields need to be filled",
                "aspects": Aspect.objects.all()
            })
        if not benefits:
            return HttpResponse("lack benefits")
        if int(cost) < 0 or int(time_cost) < 0:
            return render(request, "kids/add_course.html", {
                "nay_message": "Cost and time cost should not be negative",
                "aspects": Aspect.objects.all()
            })
        
        # Add new course to database
        new_course = Course(title=title, description=description, 
                            category=category, img_URL=img_URL,                            
                            cost=int(cost), starting_date=starting_date,
                            time_cost=time_cost)
        new_course.save()

        # Set aspect values of the new course
        new_course.goal.set(aspects)
        new_course.save()
        
        # Redirect user to index and inform successfully
        request.session['yay_message'] = "Create course successfully"
        return HttpResponseRedirect(reverse("kids:index"))

    # If user clicking link or being redirect
    else:
        return render(request, "kids/add_course.html", {
            "aspects": Aspect.objects.all()
        })


@login_required
def add_kid(request):
    # If user submit form
    if request.method == "POST":
        # Define variables
        nickname = request.POST['nickname']
        full_name = request.POST['full_name']
        birthday = request.POST['birthday']
        parent = User.objects.get(username=request.user.username)
        gender = request.POST['gender']

        # Check condition
        if not nickname or not full_name or not birthday or not gender:
            return render(request, "kids/add_kid.html", {
                "nay_message": "All fields required!"
            })

        # Add new kid to database
        new_kid = Kid(nickname=nickname, full_name=full_name, birthday=birthday, parent=parent, gender=gender, status=3)
        new_kid.save()

        # Redirect user to index and inform successfully
        request.session['yay_message'] = "Add kid successfully"
        return HttpResponseRedirect(reverse("kids:index"))

    # If user clicking link or being redirect
    else:
        return render(request, "kids/add_kid.html")


@login_required
def kids(request):
    return render(request, "kids/kids.html", {
        "kids": Kid.objects.filter(parent=request.user)
    })


@login_required
def kid_detail(request, kid_id):

    try:
        # Define kid
        kid = Kid.objects.get(pk=kid_id)

    except ObjectDoesNotExist:
        return render(request, "kids/kids.html", {
            "nay_message": "Kid does not exist",
            "kids": Kid.objects.filter(parent=request.user)
        })
    kids = Kid.objects.filter(parent=request.user)
    if kid not in kids:
        return render(request, "kids/kids.html", {
            "nay_message": "You are allowed to view your kids information only!",
            "kids": Kid.objects.filter(parent=request.user)
        })

    # Define message
    if 'nay_message' not in request.session:
        request.session['nay_message'] = []

    if 'yay_message' not in request.session:
        request.session['yay_message'] = []

    nay_message = request.session['nay_message']
    yay_message = request.session['yay_message']
    
    # Clear messages
    request.session['nay_message'] = ""
    request.session['yay_message'] = ""

    # Unchanged information
    details_1 = [
        {'key':'Nick Name', 'sub':'nickname','value': kid.nickname},
        {'key':'Full Name', 'sub':'full_name','value': kid.full_name},
        {'key':'Birthday', 'sub':'birthday','value': kid.birthday},
        {'key':'Gender', 'sub':'gender','value': kid.get_gender_display}        
    ]

    # Information that change overtime and evaluation
    details_2 = [
        {'key':'Status', 'sub':'status','value': kid.get_status_display},
        {'key':'Physical Growth', 'sub':'physical_growth', 'value': kid.get_physical_growth_display},
        {'key':'Motor', 'sub':'motor','value': kid.get_motor_display},
        {'key':'Cognitive/Intellectual', 'sub':'cog_int', 'value': kid.get_cog_int_display},
        {'key':'Social Emotional', 'sub':'social_emotional', 'value': kid.get_social_emotional_display},
        {'key':'Language Communication', 'sub':'language_communication', 'value': kid.get_language_communication_display},
        {'key':'Gender Growth', 'sub':'gender_growth', 'value': kid.get_gender_growth_display},
        {'key':'Race', 'sub': 'race', 'value': kid.get_race_display}
    ]

    
    
    return render(request, "kids/kid_detail.html", {
        "details_1": details_1,
        "details_2": details_2,
        "kid": kid,
        "nay_message": nay_message,
        "yay_message": yay_message
    })


@login_required
def kid_evaluate(request):
    if request.method == "POST":
        current_date = str(date.today())
        id = request.POST['id']
        kid = Kid.objects.get(pk=id)
        birthday = str(kid.birthday)
        age = days_between(birthday, current_date)/365

        if age < 6:
            request.session['nay_message'] = "Child's age has to be older or equal to 6"
            return HttpResponseRedirect(reverse('kids:kid_detail', args=id))
            

        return render(request, "kids/evaluation.html")


# Evaluate kid and display it in kid.html
@login_required
def aspect_evaluate(request):
    if request.method == "POST":
        # Define variables
        id = request.POST['id']
        aspect = request.POST['aspect']        
        kid = Kid.objects.get(pk=id)
        field_object = Kid._meta.get_field(aspect)
        field_value = field_object.value_from_object(kid)

        return HttpResponse(f"{field_value}")

