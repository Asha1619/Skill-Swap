from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from django.conf import settings
from django.utils import timezone
import uuid
import razorpay




def register_options(request):
    return render(request, "register.html")



def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        full_name = request.POST.get("full_name", "")

        # Validation
        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})
        
        if len(password) < 6:
            return render(request, "register.html", {"error": "Password must be at least 6 characters"})

        if Profile.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        if Profile.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email already exists"})

        # Create User
        Profile.objects.create(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            bio="",
            location=""
        )

        messages.success(request, "✅ Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")


def tutor_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        full_name = request.POST.get("full_name", "")
        expertise = request.POST.get("expertise", "")
        bio = request.POST.get("bio", "")

        # Validation
        if password != confirm_password:
            return render(request, "tutor_register.html", {"error": "Passwords do not match"})
        
        if len(password) < 6:
            return render(request, "tutor_register.html", {"error": "Password must be at least 6 characters"})

        if Tutor.objects.filter(username=username).exists():
            return render(request, "tutor_register.html", {"error": "Username already exists"})

        if Tutor.objects.filter(email=email).exists():
            return render(request, "tutor_register.html", {"error": "Email already exists"})

        # Create Tutor
        Tutor.objects.create(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            expertise=expertise,
            bio=bio
        )

        messages.success(request, "✅ Tutor account created successfully! Please login.")
        return redirect("login")

    return render(request, "tutor_register.html")

def user_register(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")


        # Check password
        if password != confirm_password:

            return render(
                request,
                "user_register.html",
                {
                    "error": "Passwords do not match"
                }
            )


        # Check username
        if Profile.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "user_register.html",
                {
                    "error": "Username already exists"
                }
            )


        # Check email
        if Profile.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                "user_register.html",
                {
                    "error": "Email already exists"
                }
            )


        # Create user
        Profile.objects.create(
            full_name=full_name,
            username=username,
            email=email,
            password=password,
            bio="",
            location=""
        )


        # Registration successful
        return redirect("login")


    return render(
        request,
        "user_register.html")


def login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")



        Adminemail = "admin@gmail.com"
        Adminpass = "1234"

        if email == Adminemail and password == Adminpass:

            request.session["admin"] = True

            return redirect("admin_dashboard")


  
        try:

            tutor = Tutor.objects.get(
                email=email,
                password=password
            )

            request.session["tutor_id"] = tutor.id

            return redirect("tutor_dashboard")

        except Tutor.DoesNotExist:

            pass


      
        try:

            user = Profile.objects.get(
                email=email,
                password=password
            )

            request.session["user_id"] = user.id

            return redirect("dashboard")

        except Profile.DoesNotExist:

            return render(
                request,
                "login.html",
                {
                    "error": "Invalid email or password"
                }
            )


    return render(request, "login.html")



def dashboard(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

    except Profile.DoesNotExist:
        return redirect("login")


    # ==============================
    # MY SKILLS
    # ==============================

    user_teaches = user.profile_skills.filter(
        skill_type="teach"
    )

    user_learns = user.profile_skills.filter(
        skill_type="learn"
    )


    # ==============================
    # OTHER USERS
    # ==============================

    other_users = Profile.objects.exclude(
        id=user_id
    )


    # ==============================
    # ALL SKILLS
    # ==============================

    all_skills = Skill.objects.all()


    # ==============================
    # TOTAL USERS
    # ==============================

    total_users = Profile.objects.count()


    # ==============================
    # PENDING SWAP REQUESTS
    # ==============================

    pending_requests_count = SkillSwapRequest.objects.filter(
        to_user=user,
        status="pending"
    ).count()


    # ==============================
    # AVAILABLE MOCK TESTS
    # ==============================

    available_mock_tests = MockTest.objects.filter(
        status="active"
    )


    # ==============================
    # CERTIFICATE REQUESTS
    # ==============================

    certificate_requests = CertificateRequest.objects.filter(
        student=user
    ).select_related(
        "test",
        "tutor",
        "attempt"
    ).order_by(
        "-requested_at"
    )


    # ==============================
    # CERTIFICATES
    # ==============================

    certificates = Certificate.objects.filter(
        student=user
    ).select_related(
        "test",
        "tutor"
    ).order_by(
        "-issued_date"
    )


    # ==============================
    # OTHER USERS' SKILLS
    # ==============================

    for other in other_users:

        other.teaches_skills = other.profile_skills.filter(
            skill_type="teach"
        )

        other.learns_skills = other.profile_skills.filter(
            skill_type="learn"
        )


    # ==============================
    # CONTEXT
    # ==============================

    context = {

        "user": user,

        "user_teaches": user_teaches,

        "user_learns": user_learns,

        "other_users": other_users,

        "all_skills": all_skills,

        "total_users": total_users,

        "pending_requests_count":
            pending_requests_count,

        "available_mock_tests":
            available_mock_tests,

        "certificate_requests":
            certificate_requests,

        "certificates":
            certificates,
    }


    return render(
        request,
        "dashboard.html",
        context
    )




def profile(request):
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]
    user = Profile.objects.get(id=user_id)

    # All available skills
    all_skills = Skill.objects.all()

    if request.method == "POST":
        # Update personal details
        user.full_name = request.POST.get("full_name")
        user.location = request.POST.get("location")
        user.bio = request.POST.get("bio")
        user.save()

        # Get removed skills
        removed_teach = request.POST.get("removed_teach_skills", "")
        removed_learn = request.POST.get("removed_learn_skills", "")
        
        # Remove old skill selections (will be recreated)
        ProfileSkill.objects.filter(profile=user).delete()

        # Skills user can teach
        teach_skills = request.POST.getlist("teach_skills")
        
        for skill_value in teach_skills:
            if skill_value:
                # Check if it's an ID or a new skill name
                try:
                    # Try to get skill by ID
                    skill = Skill.objects.get(id=int(skill_value))
                except (ValueError, Skill.DoesNotExist):
                    # If not a valid ID, treat as new skill name
                    skill_name = skill_value.strip()
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(name=skill_name)
                
                # Create the profile skill
                ProfileSkill.objects.create(
                    profile=user,
                    skill=skill,
                    skill_type="teach"
                )

        # Skills user wants to learn
        learn_skills = request.POST.getlist("learn_skills")
        
        for skill_value in learn_skills:
            if skill_value:

                try:
                    
                    skill = Skill.objects.get(id=int(skill_value))
                except (ValueError, Skill.DoesNotExist):
                    skill_name = skill_value.strip()
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(name=skill_name)
                
                # Create the profile skill
                ProfileSkill.objects.create(
                    profile=user,
                    skill=skill,
                    skill_type="learn"
                )

        messages.success(request, "✅ Profile updated successfully!")
        return redirect("profile")

    # Existing teaching skills
    teaching_skills = ProfileSkill.objects.filter(
        profile=user,
        skill_type="teach"
    )

    # Existing learning skills
    learning_skills = ProfileSkill.objects.filter(
        profile=user,
        skill_type="learn"
    )

    context = {
        "user": user,
        "all_skills": all_skills,
        "teaching_skills": teaching_skills,
        "learning_skills": learning_skills,
    }

    return render(request, "profile.html", context)







def view_profile(request, user_id):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = Profile.objects.get(id=request.session["user_id"])
    viewing_user = get_object_or_404(Profile, id=user_id)
    
    # Get viewing user's skills
    viewing_teaches = ProfileSkill.objects.filter(profile=viewing_user, skill_type='teach')
    viewing_learns = ProfileSkill.objects.filter(profile=viewing_user, skill_type='learn')
    
    # Get current user's teaching skills (for the request form)
    current_user_teaches = ProfileSkill.objects.filter(profile=current_user, skill_type='teach')
    
    # Check for skill matches
    current_user_learn_skills = ProfileSkill.objects.filter(profile=current_user, skill_type='learn').values_list('skill_id', flat=True)
    viewing_user_teach_skills = ProfileSkill.objects.filter(profile=viewing_user, skill_type='teach').values_list('skill_id', flat=True)
    has_match = bool(set(current_user_learn_skills).intersection(set(viewing_user_teach_skills)))
    
    context = {
        "current_user": current_user,
        "viewing_user": viewing_user,
        "viewing_teaches": viewing_teaches,
        "viewing_learns": viewing_learns,
        "current_user_teaches": current_user_teaches,
        "has_match": has_match,
    }
    
    return render(request, "view_profile.html", context)



def send_request(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    if request.method == "POST":
        from_user = Profile.objects.get(id=request.session["user_id"])
        to_user_id = request.POST.get("to_user_id")
        skill_to_learn_id = request.POST.get("skill_to_learn_id")
        message = request.POST.get("message", "")
        
        to_user = get_object_or_404(Profile, id=to_user_id)
        skill_to_learn = get_object_or_404(Skill, id=skill_to_learn_id)
        
        # Check if request already exists
        existing_request = SkillSwapRequest.objects.filter(
            from_user=from_user,
            to_user=to_user,
            skill_to_learn=skill_to_learn,
            status='pending'
        ).exists()
        
        if existing_request:
            messages.warning(request, "⚠️ You already have a pending request for this skill!")
            return redirect("view_profile", user_id=to_user.id)
        
        # Create the swap request (without skill_to_teach)
        SkillSwapRequest.objects.create(
            from_user=from_user,
            to_user=to_user,
            skill_to_learn=skill_to_learn,
            message=message,
            status='pending'
        )
        
        messages.success(request, f"✅ Skill swap request sent to {to_user.full_name or to_user.username}!")
        return redirect("view_profile", user_id=to_user.id)
    
    return redirect("dashboard")








def swap_requests(request):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]
    user = Profile.objects.get(id=user_id)

    received_requests = SkillSwapRequest.objects.filter(to_user=user).order_by("-created_at")
    sent_requests = SkillSwapRequest.objects.filter(from_user=user).order_by("-created_at")

    context = {
        "user": user,
        "received_requests": received_requests,
        "sent_requests": sent_requests,
    }

    return render(request,"swap_requests.html",context)





def logout(request):
    if "user_id" in request.session:
        del request.session["user_id"]
    if "admin" in request.session:
        del request.session["admin"]
    return redirect("login")




def admin_dashboard(request):

    if "admin" not in request.session:
        return redirect("login")

    total_users = Profile.objects.count()
    total_skills = Skill.objects.count()
    total_teachers = ProfileSkill.objects.filter(
        skill_type="teach"
    ).values("profile").distinct().count()

    total_learners = ProfileSkill.objects.filter(
        skill_type="learn"
    ).values("profile").distinct().count()

    context = {
        "total_users": total_users,
        "total_skills": total_skills,
        "total_teachers": total_teachers,
        "total_learners": total_learners,
    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )





def tutor_register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        full_name = request.POST.get("full_name")
        qualification = request.POST.get("qualification")
        specialization = request.POST.get("specialization")
        experience = request.POST.get("experience")
        bio = request.POST.get("bio")
        location = request.POST.get("location")


        # Check tutor username

        if Tutor.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "tutor_register.html",
                {
                    "error":
                    "Tutor username already exists"
                }
            )


        # Check tutor email

        if Tutor.objects.filter(
            email=email
        ).exists():

            return render(request,"tutor_register.html",
                {
                    "error":
                    "Tutor email already exists"
                }
            )


        # Create tutor

        Tutor.objects.create(

            username=username,
            email=email,
            password=password,

            full_name=full_name,
            qualification=qualification,
            specialization=specialization,
            experience=experience or 0,

            bio=bio,
            location=location
        )


        return redirect("login")


    return render( request,"tutor_register.html")



def tutor_dashboard(request):

    if "tutor_id" not in request.session:
        return redirect("tutor_login")

    tutor_id = request.session["tutor_id"]

    try:
        tutor = Tutor.objects.get(id=tutor_id)
    except Tutor.DoesNotExist:
        return redirect("tutor_login")

    # ==============================
    # MOCK TESTS CREATED BY TUTOR
    # ==============================

    tutor_tests = MockTest.objects.filter(
        tutor=tutor
    ).order_by("-created_at")

    total_tests = tutor_tests.count()

    recent_tests = tutor_tests[:5]

    # ==============================
    # CERTIFICATE REQUESTS
    # ==============================

    certificate_requests = CertificateRequest.objects.filter(
        tutor=tutor
    ).select_related(
        "student",
        "test",
        "attempt"
    ).order_by("-requested_at")

    pending_certificate_count = certificate_requests.filter(
        status="pending"
    ).count()

    # ==============================
    # CERTIFICATES
    # ==============================

    tutor_certificates = Certificate.objects.filter(
        tutor=tutor
    ).select_related(
        "student",
        "test"
    ).order_by("-issued_date")

    total_certificates = tutor_certificates.count()

    recent_certificates = tutor_certificates[:5]

    # ==============================
    # STUDENTS
    # ==============================

    # Students who attempted this tutor's tests

    student_ids = TestAttempt.objects.filter(
        test__tutor=tutor
    ).values_list(
        "student_id",
        flat=True
    ).distinct()

    recent_students = Profile.objects.filter(
        id__in=student_ids
    ).order_by("-created_at")[:5]

    total_students = Profile.objects.filter(
        id__in=student_ids
    ).count()

    # ==============================
    # PENDING TEST ATTEMPTS
    # ==============================

    pending_tests = TestAttempt.objects.filter(
        test__tutor=tutor
    ).count()

    # ==============================
    # DASHBOARD
    # ==============================

    context = {

        "tutor": tutor,

        "total_students": total_students,

        "total_tests": total_tests,

        "total_certificates": total_certificates,

        "pending_tests": pending_tests,

        "recent_students": recent_students,

        "recent_tests": recent_tests,

        "certificate_requests": certificate_requests,

        "pending_certificate_count": pending_certificate_count,

        "recent_certificates": recent_certificates,
    }

    return render(
        request,
        "tutor_dashboard.html",
        context
    )





def accept_swap_request(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

        if request.method == "POST":

            swap_request = SkillSwapRequest.objects.get(
                id=request_id,
                to_user=user,
                status="pending"
            )

            swap_request.status = "accepted"
            swap_request.save()

    except Profile.DoesNotExist:
        return redirect("login")

    except SkillSwapRequest.DoesNotExist:
        pass

    return redirect("swap_requests")






def reject_swap_request(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

        if request.method == "POST":

            swap_request = SkillSwapRequest.objects.get(id=request_id,to_user=user,status="pending")

            swap_request.status = "rejected"
            swap_request.save()

    except Profile.DoesNotExist:
        return redirect("login")

    except SkillSwapRequest.DoesNotExist:
        pass

    return redirect("swap_requests")






def schedule_meeting(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

        swap_request = SkillSwapRequest.objects.get(
            id=request_id,
            status="accepted"
        )

    except Profile.DoesNotExist:
        return redirect("login")

    except SkillSwapRequest.DoesNotExist:
        return redirect("swap_requests")

    # Check whether logged-in user is part of this swap
    if swap_request.from_user != user and swap_request.to_user != user:
        return redirect("swap_requests")

    # Check if meeting already exists
    try:
        meeting = SwapMeeting.objects.get(
            swap_request=swap_request
        )
    except SwapMeeting.DoesNotExist:
        meeting = None

    if request.method == "POST":

        meeting_date = request.POST.get("meeting_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        meeting_link = request.POST.get("meeting_link")
        notes = request.POST.get("notes")

        if meeting:

            meeting.meeting_date = meeting_date
            meeting.start_time = start_time
            meeting.end_time = end_time
            meeting.meeting_link = meeting_link
            meeting.notes = notes

            meeting.save()

        else:

            SwapMeeting.objects.create(
                swap_request=swap_request,
                meeting_date=meeting_date,
                start_time=start_time,
                end_time=end_time,
                meeting_link=meeting_link,
                notes=notes
            )

        return redirect("swap_requests")

    context = {
        "user": user,
        "swap_request": swap_request,
        "meeting": meeting,
    }

    return render(request,"schedule_meeting.html",context)







def create_mock_test(request):

    if "tutor_id" not in request.session:
        return redirect("login")

    tutor_id = request.session["tutor_id"]

    tutor = Tutor.objects.get(id=tutor_id)

    skills = Skill.objects.all()

    if request.method == "POST":

        title = request.POST.get("title")
        skill_id = request.POST.get("skill")
        description = request.POST.get("description")
        difficulty = request.POST.get("difficulty")
        total_questions = request.POST.get("total_questions")
        passing_score = request.POST.get("passing_score")
        duration_minutes = request.POST.get("duration_minutes")
        marks_per_question = request.POST.get("marks_per_question")
        show_result_immediately = ( request.POST.get("show_result_immediately") == "on" )

        skill = None

        if skill_id:
            skill = Skill.objects.get(id=skill_id)

        mock_test = MockTest.objects.create(
            tutor=tutor,
            title=title,
            skill=skill,
            description=description,
            difficulty=difficulty,
            total_questions=total_questions,
            passing_score=passing_score,
            duration_minutes=duration_minutes,
            marks_per_question=marks_per_question,
            show_result_immediately=show_result_immediately,
            status="draft",
            questions=[]
        )

        return redirect("add_mock_questions",test_id=mock_test.id )

    context = {
        "tutor": tutor,
        "skills": skills,
    }

    return render(request,"mock_test_settings.html",context)






def add_mock_questions(request, test_id):

    if "tutor_id" not in request.session:
        return redirect("login")

    tutor_id = request.session["tutor_id"]

    try:
        tutor = Tutor.objects.get(id=tutor_id)

        mock_test = MockTest.objects.get(
            id=test_id,
            tutor=tutor
        )

    except (Tutor.DoesNotExist, MockTest.DoesNotExist):
        return redirect("tutor_dashboard")

    question_numbers = range(
        1,
        mock_test.total_questions + 1
    )

    if request.method == "POST":

        questions = []

        for i in question_numbers:

            question = {
                "question": request.POST.get(
                    f"question_{i}"
                ),

                "option_a": request.POST.get(
                    f"option_a_{i}"
                ),

                "option_b": request.POST.get(
                    f"option_b_{i}"
                ),

                "option_c": request.POST.get(
                    f"option_c_{i}"
                ),

                "option_d": request.POST.get(
                    f"option_d_{i}"
                ),

                "correct_answer": request.POST.get(
                    f"correct_answer_{i}"
                )
            }

            questions.append(question)

        mock_test.questions = questions
        mock_test.save()

        return redirect(
            "preview_mock_test",
            test_id=mock_test.id
        )

    return render(
        request,
        "add_mock_questions.html",
        {
            "mock_test": mock_test,
            "question_numbers": question_numbers,
        }
    )





def preview_mock_test(request, test_id):

    if "tutor_id" not in request.session:
        return redirect("login")


    tutor_id = request.session["tutor_id"]


    try:

        tutor = Tutor.objects.get(id=tutor_id)

        mock_test = MockTest.objects.get(
            id=test_id,
            tutor=tutor
        )

    except (Tutor.DoesNotExist, MockTest.DoesNotExist):

        return redirect("tutor_dashboard")


    questions = mock_test.questions


    context = {
        "mock_test": mock_test,
        "questions": questions,
    }


    return render(
        request,
        "preview_mock_test.html",
        context
    )







def publish_mock_test(request, test_id):

    if "tutor_id" not in request.session:
        return redirect("login")


    tutor_id = request.session["tutor_id"]


    try:

        tutor = Tutor.objects.get(id=tutor_id)

        mock_test = MockTest.objects.get(
            id=test_id,
            tutor=tutor
        )

    except (Tutor.DoesNotExist, MockTest.DoesNotExist):

        return redirect("tutor_dashboard")


    if request.method == "POST":

        if not mock_test.questions:

            return redirect(
                "add_mock_questions",
                test_id=mock_test.id
            )


        if len(mock_test.questions) != mock_test.total_questions:

            return redirect(
                "add_mock_questions",
                test_id=mock_test.id
            )


        mock_test.status = "active"

        mock_test.save()


    return redirect("tutor_dashboard")








def attempt_mock_test(request, test_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

        mock_test = MockTest.objects.get(
            id=test_id,
            status="active"
        )

    except Profile.DoesNotExist:
        return redirect("login")

    except MockTest.DoesNotExist:
        return redirect("dashboard")


    questions = mock_test.questions



    if request.method == "GET":

        return render(
            request,
            "attempt_mock_test.html",
            {
                "user": user,
                "mock_test": mock_test,
            }
        )


    score = 0
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0

    results = []


    answer_map = {
        "A": "option_a",
        "B": "option_b",
        "C": "option_c",
        "D": "option_d",
    }


    for index, question in enumerate(questions):

        user_answer = request.POST.get(
            f"question_{index}"
        )

        correct_answer = question.get(
            "correct_answer"
        )

        correct_option = answer_map.get(
            str(correct_answer).upper()
        )


        if not user_answer:

            unanswered_count += 1

            is_correct = False


        elif user_answer == correct_option:

            score += mock_test.marks_per_question

            correct_count += 1

            is_correct = True


        else:

            wrong_count += 1

            is_correct = False


        results.append({

            "question": question["question"],

            "option_a": question["option_a"],
            "option_b": question["option_b"],
            "option_c": question["option_c"],
            "option_d": question["option_d"],

            "user_answer": user_answer,

            "correct_answer": correct_option,

            "is_correct": is_correct,

        })


    total_marks = (
        len(questions)
        * mock_test.marks_per_question
    )


    if total_marks > 0:

        percentage = (
            score / total_marks
        ) * 100

    else:

        percentage = 0


    passed = (
        percentage >= mock_test.passing_score
    )

    TestAttempt.objects.create(
      student=user,
      test=mock_test,
      score=score,
      passed=passed
)


    return render(
        request,
        "mock_test_result.html",
        {

            "user": user,

            "mock_test": mock_test,

            "score": score,

            "total_marks": total_marks,

            "percentage": percentage,

            "correct_count": correct_count,

            "wrong_count": wrong_count,

            "unanswered_count": unanswered_count,

            "passed": passed,

            "results": results,

        }
    )







def my_test_attempts(request):

    if "user_id" not in request.session:
        return redirect("login")


    user_id = request.session["user_id"]


    try:

        user = Profile.objects.get(
            id=user_id
        )

    except Profile.DoesNotExist:

        return redirect("login")


    attempts = TestAttempt.objects.filter(
        student=user
    ).select_related(
        "test"
    ).order_by(
        "-attempted_at"
    )


    return render(
        request,
        "my_test_attempts.html",
        {
            "user": user,
            "attempts": attempts,
        }
    )




def view_test_results(request, test_id):

    # Check student login
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        user = Profile.objects.get(id=user_id)

        mock_test = MockTest.objects.get(
            id=test_id
        )

    except Profile.DoesNotExist:
        return redirect("login")

    except MockTest.DoesNotExist:
        return redirect("dashboard")

    # Get all attempts of this student for this test
    attempts = TestAttempt.objects.filter(
        student=user,
        test=mock_test
    ).order_by("-attempted_at")

    # Calculate total marks using actual questions
    total_questions = len(mock_test.questions)

    total_marks = (
        total_questions *
        mock_test.marks_per_question
    )

    # Calculate percentage for every attempt
    for attempt in attempts:

        if total_marks > 0:

            attempt.percentage = round(
                (attempt.score / total_marks) * 100,
                2
            )

        else:

            attempt.percentage = 0

    # Latest attempt
    latest_attempt = attempts.first()

    # Check whether certificate has already been requested
    certificate_requested = False

    if latest_attempt and latest_attempt.passed:

        certificate_requested = CertificateRequest.objects.filter(
            student=user,
            test=mock_test
        ).exists()

    # Send data to template
    return render(
        request,
        "view_test_results.html",
        {
            "user": user,
            "mock_test": mock_test,
            "attempts": attempts,
            "total_marks": total_marks,
            "latest_attempt": latest_attempt,
            "certificate_requested": certificate_requested,
        }
    )




def request_certificate(request, test_id):

    # Check student login
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        student = Profile.objects.get(id=user_id)
        mock_test = MockTest.objects.get(id=test_id)

    except Profile.DoesNotExist:
        return redirect("login")

    except MockTest.DoesNotExist:
        return redirect("dashboard")

    # Get latest attempt
    attempt = TestAttempt.objects.filter(student=student,test=mock_test).order_by("-attempted_at").first()

    # No attempt
    if not attempt:
        return redirect("view_test_results",test_id=test_id)

    # Student must pass
    if not attempt.passed:
        return redirect(
            "view_test_results",
            test_id=test_id
        )

    # Check existing certificate request
    existing_request = CertificateRequest.objects.filter(
        student=student,
        test=mock_test
    ).first()

    if existing_request:
        return redirect("view_test_results",test_id=test_id)

    # Create certificate request
    CertificateRequest.objects.create(
        student=student,
        test=mock_test,
        tutor=mock_test.tutor,
        attempt=attempt,
        status="pending"
    )

    return redirect("view_test_results",test_id=test_id)




def tutor_certificate_requests(request):

    if "tutor_id" not in request.session:
        return redirect("tutor_login")

    tutor_id = request.session["tutor_id"]

    try:
        tutor = Tutor.objects.get(
            id=tutor_id
        )

    except Tutor.DoesNotExist:
        return redirect("tutor_login")

    certificate_requests = CertificateRequest.objects.filter(
        tutor=tutor
    ).select_related(
        "student",
        "test",
        "attempt"
    ).order_by("-requested_at")

    return render(
        request,
        "tutor_certificate_requests.html",
        {
            "tutor": tutor,
            "certificate_requests": certificate_requests,
        }
    )




def approve_certificate_request(request, request_id):

    if "tutor_id" not in request.session:
        return redirect("tutor_login")

    tutor_id = request.session["tutor_id"]

    try:
        tutor = Tutor.objects.get(
            id=tutor_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            tutor=tutor
        )

    except Tutor.DoesNotExist:
        return redirect("tutor_login")

    except CertificateRequest.DoesNotExist:
        return redirect("tutor_certificate_requests")

    # Approve request
    certificate_request.status = "approved"
    certificate_request.save()

    return redirect(
        "tutor_certificate_requests"
    )




def reject_certificate_request(request, request_id):

    if "tutor_id" not in request.session:
        return redirect("tutor_login")

    tutor_id = request.session["tutor_id"]

    try:

        tutor = Tutor.objects.get(
            id=tutor_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            tutor=tutor
        )

    except Tutor.DoesNotExist:

        return redirect("tutor_login")

    except CertificateRequest.DoesNotExist:

        return redirect("tutor_dashboard")

    certificate_request.status = "rejected"

    certificate_request.save()

    return redirect( "tutor_dashboard" )



def certificate_payment(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:

        student = Profile.objects.get(
            id=user_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            student=student
        )

    except Profile.DoesNotExist:

        return redirect("login")

    except CertificateRequest.DoesNotExist:

        return redirect("student_dashboard")


    # Payment is allowed only after tutor approval

    if certificate_request.status != "approved":

        return redirect("dashboard")


    return render(
        request,
        "certificate_payment.html",
        {
            "student": student,
            "certificate_request": certificate_request,
            "amount": 199,
        }
    )





def certificate_payment(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")


    user_id = request.session["user_id"]


    try:

        student = Profile.objects.get(
            id=user_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            student=student
        )

    except Profile.DoesNotExist:

        return redirect("login")

    except CertificateRequest.DoesNotExist:

        return redirect("dashboard")


    # Only approved requests can be paid

    if certificate_request.status != "approved":

        messages.error(
            request,
            "This certificate is not available for payment."
        )

        return redirect("dashboard")


    # Certificate price

    amount = 199

    # Razorpay requires amount in paise

    amount_in_paise = amount * 100


    # Razorpay client

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


    # Create Razorpay order

    order_data = {

        "amount": amount_in_paise,

        "currency": "INR",

        "receipt":
            f"certificate_{certificate_request.id}",

        "notes": {

            "certificate_request_id":
                str(certificate_request.id),

            "student_id":
                str(student.id),

            "test_id":
                str(certificate_request.test.id)

        }

    }


    try:

        razorpay_order = client.order.create(
            data=order_data
        )

    except Exception as e:

        print(
            "Razorpay order error:",
            e
        )

        messages.error(
            request,
            "Unable to create payment order."
        )

        return redirect("dashboard")


    # Save order ID

    certificate_request.razorpay_order_id = (
        razorpay_order["id"]
    )

    certificate_request.payment_amount = amount

    certificate_request.save()


    context = {

        "student":
            student,

        "certificate_request":
            certificate_request,

        "razorpay_order_id":
            razorpay_order["id"],

        "razorpay_key":
            settings.RAZORPAY_KEY_ID,

        "amount":
            amount_in_paise,

        "amount_rupees":
            amount,

    }


    return render(
        request,
        "certificate_payment.html",
        context
    )







def process_certificate_payment(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")


    if request.method != "POST":
        return redirect("dashboard")


    user_id = request.session["user_id"]


    try:

        student = Profile.objects.get(
            id=user_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            student=student
        )

    except Profile.DoesNotExist:

        return redirect("login")

    except CertificateRequest.DoesNotExist:

        return redirect("dashboard")


    # Payment allowed only after tutor approval

    if certificate_request.status != "approved":

        messages.error(
            request,
            "This certificate is not available for payment."
        )

        return redirect("dashboard")


    # Get Razorpay response

    razorpay_payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    razorpay_signature = request.POST.get(
        "razorpay_signature"
    )


    # Make sure all values exist

    if not all([
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature
    ]):

        messages.error(
            request,
            "Invalid payment response."
        )

        return redirect("dashboard")


    # IMPORTANT:
    # Compare with the order created by YOUR server

    if razorpay_order_id != certificate_request.razorpay_order_id:

        messages.error(
            request,
            "Invalid Razorpay order."
        )

        return redirect("dashboard")


    # Create Razorpay client

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


    # Verify Razorpay signature

    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id":
                certificate_request.razorpay_order_id,

            "razorpay_payment_id":
                razorpay_payment_id,

            "razorpay_signature":
                razorpay_signature

        })

    except razorpay.errors.SignatureVerificationError:

        messages.error(
            request,
            "Payment verification failed."
        )

        return redirect("dashboard")

    except Exception as e:

        print(
            "Razorpay verification error:",
            e
        )

        messages.error(
            request,
            "Unable to verify payment."
        )

        return redirect("dashboard")


    # Check actual payment status

    try:

        payment = client.payment.fetch(
            razorpay_payment_id
        )

        if payment["status"] != "captured":

            messages.error(
                request,
                "Payment is not captured yet."
            )

            return redirect("dashboard")

    except Exception as e:

        print(
            "Payment status error:",
            e
        )

        messages.error(
            request,
            "Unable to confirm payment."
        )

        return redirect("dashboard")


    # ---------------------------------
    # PAYMENT SUCCESSFUL
    # ---------------------------------

    certificate_request.razorpay_payment_id = (
        razorpay_payment_id
    )

    certificate_request.status = "paid"

    certificate_request.paid_at = timezone.now()

    certificate_request.save()


    # Generate certificate

    return redirect(
        "generate_certificate",
        request_id=certificate_request.id
    )





def generate_certificate(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:

        student = Profile.objects.get(
            id=user_id
        )

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            student=student
        )

    except Profile.DoesNotExist:

        return redirect("login")

    except CertificateRequest.DoesNotExist:

        return redirect("dashboard")


    # Certificate can only be generated after payment
    if certificate_request.status != "paid":

        return redirect("dashboard")


    # Check if certificate already exists
    existing_certificate = Certificate.objects.filter(
        student=student,
        test=certificate_request.test
    ).first()

    if existing_certificate:

        certificate_request.status = "completed"
        certificate_request.save()

        return redirect(
            "view_certificate",
            request_id=certificate_request.id
        )


    attempt = certificate_request.attempt


    certificate = Certificate.objects.create(

        student=student,

        test=certificate_request.test,

        score=attempt.score,

        tutor=certificate_request.tutor,

        payment_status="paid",

        certificate_name=(
            f"{student.full_name or student.username} "
            f"- {certificate_request.test.title}"
        ),

        certificate_id=(
            "CERT-"
            + uuid.uuid4().hex[:10].upper()
        )

    )


    certificate_request.status = "completed"

    certificate_request.save()


    return redirect(
        "view_certificate",
        request_id=certificate_request.id
    )





def view_certificate(request, request_id):

    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session["user_id"]

    try:
        student = Profile.objects.get(id=user_id)

        certificate_request = CertificateRequest.objects.get(
            id=request_id,
            student=student,
            status="completed"
        )

        certificate = Certificate.objects.get(
            student=student,
            test=certificate_request.test
        )

    except Profile.DoesNotExist:
        return redirect("login")

    except CertificateRequest.DoesNotExist:
        return redirect("dashboard")

    except Certificate.DoesNotExist:
        return redirect("dashboard")

    return render(
        request,
        "view_certificate.html",
        {
            "student": student,
            "certificate": certificate,
            "certificate_request": certificate_request,
        }
    )