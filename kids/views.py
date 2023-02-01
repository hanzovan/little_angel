from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .helpers import strong_password, days_between
from datetime import datetime, timedelta, date

from django.contrib.auth import authenticate, login, logout

from .models import User, Kid, Course, Aspect, Evaluation, Expectation, Time_to_spend
from django.contrib.auth.decorators import login_required

# Import error handler
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError


# Add wrapper
def monthly_refresh(f):
    def wrapper(request, *args, **kwargs):

        # If user logged in
        if request.user.is_authenticated:
            user = User.objects.get(username = request.user.username)

            today = date.today()

            if not user.next_refresh_date:
                user.next_refresh_date = date.today()

            days = days_between(str(today), str(user.next_refresh_date))

            # If date is the date need to refresh, the system refresh date itself
            if days <= 0:
                
                time_to_spends = Time_to_spend.objects.filter(kid__parent=user)
                for time_to_spend in time_to_spends:
                    time_to_spend.duration = time_to_spend.course.time_cost
                    time_to_spend.save()

                # Adjust refresh date for only this user
                user.last_refresh_date = today
                user.next_refresh_date = user.last_refresh_date + timedelta(days=28)
                user.save()

                request.session['yay_message'] = 'Time to spend was refreshed today!'        

        return f(request, *args, **kwargs)
    return wrapper


@monthly_refresh
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
@monthly_refresh
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
@monthly_refresh
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
@monthly_refresh
def kids(request):
    return render(request, "kids/kids.html", {
        "kids": Kid.objects.filter(parent=request.user)
    })


@login_required
@monthly_refresh
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

    courses = kid.learner.all()

    # Calculate all cost for all course of this kid
    cost = sum(i.cost for i in courses)

    # Define timing
    time_to_spends = kid.timing.all()

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
        {'key':'Gender', 'sub':'gender','value': kid.get_gender_display},
        {'key':'Free time per week', 'sub':'time', 'value': kid.time/4}      
    ]

    # Information that change overtime and evaluation
    details_2 = [        
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
        "courses": courses,
        "cost": cost,
        "time_to_spends": time_to_spends,
        "nay_message": nay_message,
        "yay_message": yay_message
    })
    

# Evaluate kid and display it in kid.html
@login_required
@monthly_refresh
def aspect_evaluate(request):
    if request.method == "POST":
        # Define variables
        id = request.POST['id']
        aspect = request.POST['aspect']        
        kid = Kid.objects.get(pk=id)
        field_object = Kid._meta.get_field(aspect)
        field_value = field_object.value_from_object(kid)
        field_display = kid._get_FIELD_display(field_object)

        details_2 = [
        {'key':'Physical Growth', 'sub':'physical_growth', 'value': kid.get_physical_growth_display},
        {'key':'Motor', 'sub':'motor','value': kid.get_motor_display},
        {'key':'Cognitive/Intellectual', 'sub':'cog_int', 'value': kid.get_cog_int_display},
        {'key':'Social Emotional', 'sub':'social_emotional', 'value': kid.get_social_emotional_display},
        {'key':'Language Communication', 'sub':'language_communication', 'value': kid.get_language_communication_display},
        {'key':'Gender Growth', 'sub':'gender_growth', 'value': kid.get_gender_growth_display},
        {'key':'Race', 'sub': 'race', 'value': kid.get_race_display}
    ]

        def getKey(my_list, sub_key):
            for i in my_list:
                if i['sub'] == sub_key:
                    the_key = i['key']
            return the_key

        aspect_name = getKey(details_2, aspect)
        
        # Get the aspect
        this_aspect = Aspect.objects.get(title__contains=aspect_name)

        # Get the courses that related to this aspect
        related_courses = this_aspect.target.all()
        
        # Get the courses that this kid is currently studying
        current_courses = kid.learner.all()

        # Get the courses that related to this aspect but this kid did not studying yet
        proposed_courses = related_courses.difference(current_courses)



        return render(request, "kids/evaluation.html", {
            "kid": kid,
            "aspect": aspect,
            "aspect_name": aspect_name,
            "field_object": field_object,
            "field_value": field_value,
            "field_display": field_display,
            "courses": proposed_courses,
            "this_aspect": this_aspect
        })


@login_required
@monthly_refresh
def evaluation(request):
    if request.method == "POST":
        # Define variable
        id = request.POST['id']
        kid = Kid.objects.get(pk=id)
        aspect = request.POST['aspect']
        new_evaluation = request.POST['new_evaluation']

        setattr(kid, aspect, new_evaluation)
        kid.save()

        request.session['yay_message'] = "Updated aspect successfully"
        return HttpResponseRedirect(reverse('kids:kid_detail', args=id))


@login_required
@monthly_refresh
def course_detail(request, course_id):
    course = Course.objects.get(pk=course_id)
    kids = Kid.objects.filter(parent=request.user)

    # Get students list of the course who is parented by user
    students = course.student.all().intersection(kids)

    # Access non students
    non_students = kids.difference(students)

    # non_students = Kid.objects.exclude(id__in=[o.id for o in students])

    return render(request, "kids/course_detail.html", {
        "course": course,
        "kids": kids,
        "students": students,
        "non_students": non_students
    })


@login_required
@monthly_refresh
def course_register(request):
    # If form was submitted
    if request.method == "POST":
        
        # Define variables
        kid_id = request.POST['kid_id']
        course_id = request.POST['course_id']
        kid = Kid.objects.get(pk=kid_id)
        course = Course.objects.get(pk=course_id)

        # Add kid to the course
        course.student.add(kid)
        course.save()

        # Minus time available for kid
        time = kid.time
        kid.time = time - course.time_cost
        kid.save()

        # Add time to spend for the next 4 weeks
        time_to_spend = Time_to_spend(course=course, kid=kid, duration=course.time_cost)
        time_to_spend.save()

        request.session['yay_message'] = "Kid was registered to course successfully"
        return HttpResponseRedirect(reverse('kids:index'))


@login_required
@monthly_refresh
def quit_course(request):
    # If form was submitted
    if request.method == "POST":

        # Define variables
        kid_id = request.POST['kid_id']
        course_id = request.POST['course_id']
        kid = Kid.objects.get(pk=kid_id)
        course = Course.objects.get(pk=course_id)

        # Remove kid from course
        course.student.remove(kid)
        course.save()

        # Add time back to kid
        time = kid.time
        kid.time = time + course.time_cost
        kid.save()

        # Remove time to spend
        time_to_spend = Time_to_spend.objects.get(course=course, kid=kid)
        time_to_spend.delete()

        request.session['yay_message'] = "Kid was quitted from course"
        return HttpResponseRedirect(reverse('kids:index'))


# Allow user to refresh duration that need to be spent for courses for all kids
@login_required
@monthly_refresh
def refresh_duration(request):    

    # If user reach route via submiting form
    if request.method == "POST":

        # Refresh time to spend for all kids of this user
        time_to_spends = Time_to_spend.objects.filter(kid__parent=User.objects.get(username=request.user.username))
        for time_to_spend in time_to_spends:
            time_to_spend.duration = time_to_spend.course.time_cost
            time_to_spend.save()

        # Adjust refresh date for only this user
        user = User.objects.get(username=request.user.username)
        user.last_refresh_date = date.today()
        user.next_refresh_date = user.last_refresh_date + timedelta(days=28)
        user.save()

        request.session['yay_message'] = "All time to spend were refreshed"
        return HttpResponseRedirect(reverse("kids:index"))


# Allow user to spend time with one course
@login_required
@monthly_refresh
def spend_time(request):
    if request.method == "POST":
        # Define kid and course variables
        kid_id = request.POST['kid_id']

        try:
            course_id = request.POST['course_id']
        except MultiValueDictKeyError:
            request.session['nay_message'] = "You need to choose course"        
            return HttpResponseRedirect(reverse('kids:kid_detail', args=kid_id))
        
        kid = Kid.objects.get(pk=kid_id)
        
        course = Course.objects.get(pk=course_id)
        
        # Define the duration of the course that this kid have to spend for 4 weeks
        time_to_spend = Time_to_spend.objects.get(kid=kid, course=course)
        
        # Define the duration that the kid have to spend this time
        duration_today = request.POST['duration']

        # Minus duration spent today to the duration of 4 weeks
        time_to_spend.duration = time_to_spend.duration - int(duration_today)
        time_to_spend.save()

        # If time was spent over the time left
        if time_to_spend.duration <= 0:
            time_to_spend.duration = 0
            time_to_spend.save()
            request.session['yay_message'] = "Congratulation, kid finished required time for this course this month!"

        else:
            # Inform successfully and redirect to kid detail page
            request.session['yay_message'] = "Congratulation for finish today's course"
        return HttpResponseRedirect(reverse("kids:kid_detail", args=request.POST['kid_id']))

        
