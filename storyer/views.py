from typing import get_origin
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.http import HttpResponse

from storyer.models import Student, Assignment, Faculty, Course, Group, Preference
from django.contrib.auth.models import User
from .forms import LoginForm, SignupForm, CourseCreateForm, CourseChangeForm, GroupCreateForm, AssignmentCreateForm, StudentGroupChangeForm, AssignmentSubmissionForm
from django.core.management import call_command
from storyer import faculty_group_sort


def index(request):
    return render(request, 'index.html')


def signup_student(request):
    # if a user submit a form from the webpage
    if request.method == "POST":
        context = {}
        # get the data and check if its empty before trying to put it into a form model
        post_data = request.POST or None
        if post_data is not None:
            signup_form = SignupForm(post_data)
            # if the data was parsed correctly and could be put into a form object without issue
            if signup_form.is_valid():
                signup_form = signup_form.cleaned_data
                # as long as this email from the form doesnt exist for another student
                if not Student.objects.filter(email=signup_form['email']).exists():
                    # put the first and last name together
                    name = (signup_form['first_name'].replace(" ", "").title(
                    ))+" "+signup_form['last_name'].replace(" ", "").title()
                    # put the data into a new Student in the models
                    new_student = Student(
                        name=name, email=signup_form['email'], password=signup_form['password'])
                    new_student.save()
                    course = Course.objects.filter(
                        code=signup_form['course_code']).first()
                    if course:
                        new_student.courses.add(course)
                    new_student.courses.add()
                    # save the new Student and then display the view for student
                    new_student.save()
                    return redirect('storyer:student-home', student_id=new_student.id)
                else:
                    context.update({"exists": True})
        context.update({'error_message': True})
        return render(request, 'student-signup.html', context)

    return render(request, 'student-signup.html')


def signup_faculty(request):
    if request.method == "POST":
        context = {}
        post_data = request.POST or None
        if post_data is not None:
            signup_form = SignupForm(post_data)
            if signup_form.is_valid():
                signup_form = signup_form.cleaned_data
                if not Faculty.objects.filter(email=signup_form['email']).exists():
                    name = (signup_form['first_name'].replace(" ", "").title(
                    ))+" "+signup_form['last_name'].replace(" ", "").title()
                    new_faculty = Faculty(
                        name=name, email=signup_form['email'], password=signup_form['password'])
                    new_faculty.save()
                    return redirect('storyer:faculty_landing', faculty_id=new_faculty.id)
                else:
                    context.update({"exists": True})
        context.update({'error_message': True})
        return render(request, 'initial_faculty.html', context)

    return render(request, 'initial_faculty.html')


# student login only
def student_login(request):
    if request.method == "POST":
        post_data = request.POST or None
        if post_data is not None:
            login_form = LoginForm(post_data)
            if login_form.is_valid():
                login_form = login_form.cleaned_data
                # look for student in user list
                student = Student.objects.filter(
                    email=login_form['email'], password=login_form['password']).first()
                if student is not None:
                    if student.group.all() is not None:
                        return redirect('storyer:student-home', student_id=student.id)
                    return redirect('storyer:student-home', student_id=student.id)
        context = {'error_message': True}
        return render(request, 'student-login.html', context)
    return render(request, 'student-login.html')


def student_homepage(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    courses = student.courses.all()
    course = courses[0].id
    group = None
    if student.group:
        group = student.group.all()
    return render(request, 'student-home.html', {'student': student, 'course':  course, 'group': group})


def student_pick(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    groups = Group.objects.filter(course=course_id).order_by('name')
    print(groups)
    context = {
        'student': student,
        'groups': groups,
    }
    return render(request, 'student-pick.html', context)


def student_view_groups(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    groups = Group.objects.filter(course=course_id).order_by('name')
    print(groups)
    context = {
        'student': student,
        'groups': groups,
    }
    return render(request, 'student-view-groups.html', context)


def student_assignment(request, student_id, course_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)
    group = student.group.get(course=course)
    assignment = Assignment.objects.filter(group=group)
    print(group.id)
    context = {
        'student': student,
        'assignment': assignment,
        'course': course
    }
    if request.method == "POST":
        post_data = request.POST or None
        assignment_id = post_data['assignment']
        return redirect('storyer:student-submit', student_id=student.id, assignment_id=assignment_id)
    return render(request, 'student-assignment.html', context)


def submit_assignment(request, student_id, assignment_id):
    student = get_object_or_404(Student, pk=student_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    assignment_form = AssignmentSubmissionForm()
    context = {
        'student': student,
        'assignment': assignment,
        'form': assignment_form
    }
    if request.method == "POST":
        post_data = request.POST or None
        if post_data is not None:
            submission_form = AssignmentSubmissionForm(post_data)
            if submission_form.is_valid():
                try:
                    submission_form = submission_form.cleaned_data
                    assignment.zoom_link = submission_form['zoom_link']
                    assignment.video_link = submission_form['video_link']
                    assignment.slides_link = submission_form['slides_link']
                    assignment.questions_link = submission_form['questions_link']
                    assignment.save()
                    return redirect('storyer:student-post-submit/', student_id=student.id)
                except:
                    context.update({'error_message': True})
   # print(assignment)
   # print(assignment)
    return render(request, 'student-submit.html', context)


def student_post_submit(request, student_id):
    return render(request, 'student-post-submit.html', {'student_id': student_id})


def login_faculty(request):
    if request.method == "POST":
        post_data = request.POST or None
        if post_data is not None:
            login_form = LoginForm(post_data)
            if login_form.is_valid():
                login_form = login_form.cleaned_data
                # look for student in user list
                faculty = Faculty.objects.filter(
                    email=login_form['email'], password=login_form['password']).first()
                if faculty is not None:
                    # TODO: display a default course for the faculty
                    course = Course.objects.filter(creator=faculty).first()
                    if course is not None:
                        return redirect('storyer:faculty_landing', faculty_id=faculty.id, course_id=course.id)
                    return redirect('storyer:faculty_landing', faculty_id=faculty.id)

        context = {'error_message': True}
        return render(request, 'login_faculty.html', context)

    return render(request, 'login_faculty.html')


# Initial dashboard for faculty to navigate and look at all of their courses


def faculty_landing(request, faculty_id, course_id=None):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = None
    # add course details as well if one is given
    if course_id is not None:
        course = get_object_or_404(Course, pk=course_id)
    return render(request, 'faculty_landing.html', {'faculty': faculty, 'course': course})

# Let faculty accounts change which course they would like to view


def faculty_change_course(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)

    # receive the submitted form option entry from a dropdown list
    post_data = request.POST or None
    if post_data is not None:
        context = {}
        course_change_form = CourseChangeForm(
            faculty=faculty, data=post_data)
        if course_change_form.is_valid():
            course_change_form = course_change_form.cleaned_data
            # get data from the dict that the form returned
            new_id = course_change_form.get('course', "0")
            return redirect('storyer:faculty_landing', faculty_id=faculty.id, course_id=new_id)
        else:
            print(course_change_form.errors.as_data())
            context.update({'error_message': True})
    else:
        course_change_form = CourseChangeForm(faculty=faculty)

    return render(request, 'faculty_change_course.html', {'faculty': faculty, 'course': course, 'form': course_change_form})

# Displays all the assignments for every group


def faculty_check_assignments(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)
    groups = course.group_set.all()

    return render(request, 'faculty_check_assignments.html', {'faculty': faculty, 'course': course, 'groups': groups})

# Allow faculty account to create a single assignment for one group


def faculty_create_assignment(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)

    # receive the submitted form to create assignment
    post_data = request.POST or None
    if post_data is not None:
        context = {}
        assignment_create_form = AssignmentCreateForm(
            course=course, data=post_data)
        if assignment_create_form.is_valid():
            assignment_create_form = assignment_create_form.cleaned_data
            # get data from the dict that the form returned
            title = assignment_create_form.get('title', "0")
            description = assignment_create_form.get('description', "0")
            group_id = assignment_create_form.get('group', "0")
            new_assignment = Assignment(
                title=title, description=description, group=Group.objects.get(id=group_id))
            new_assignment.save()
            return redirect('storyer:faculty_check_assignments', faculty_id=faculty.id, course_id=course.id)
        else:
            print(assignment_create_form.errors.as_data())
            context.update({'error_message': True})
    else:
        assignment_create_form = AssignmentCreateForm(course=course)

    return render(request, 'faculty_create_assignment.html', {'faculty': faculty, 'course': course, 'form': assignment_create_form})

# Lets a faaculty account create a new course


def faculty_create_course(request, faculty_id, course_id=None):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    # retain course info if faculty already has one set to view
    course = None
    if course_id is not None:
        course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        context = {}
        post_data = request.POST or None
        if post_data is not None:
            course_create_form = CourseCreateForm(post_data)
            if course_create_form.is_valid():
                course_create_form = course_create_form.cleaned_data
                name = course_create_form['name']
                code = course_create_form['code']
                # check if a course this faculty member has created already exists with the same name,
                # as well as the code hasn't been used before at all
                if not Course.objects.filter(code=code).exists() and not faculty.course_set.filter(name=name).exists():
                    new_course = Course(name=name, code=code, creator=faculty)
                    new_course.save()
                    return redirect('storyer:faculty_landing', faculty_id=faculty.id, course_id=new_course.id)
                else:
                    context.update({"exists": True})
            else:
                print(course_create_form.errors.as_data())
        context.update({'error_message': True})
        return render(request, 'faculty_create_course.html', {'faculty': faculty, 'course': course})

    return render(request, 'faculty_create_course.html', {'faculty': faculty, 'course': course})

# Lets a faculty account create a group for the certain course


def faculty_create_group(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":
        context = {}
        post_data = request.POST or None
        group_create_form = GroupCreateForm(post_data)
        if post_data is not None:
            if group_create_form.is_valid():
                group_create_form = group_create_form.cleaned_data
                name = group_create_form['name']
                description = group_create_form['description']
                # check if a course this faculty member has created already exists with the same name,
                # as well as the code hasn't been used before at all
                if not course.group_set.filter(name=name).exists():
                    new_group = Group(
                        name=name, description=description, course=course)
                    new_group.save()
                    return redirect('storyer:faculty_landing', faculty_id=faculty.id, course_id=course.id)
                else:
                    context.update({"exists": True})
            else:
                print(group_create_form.errors.as_data())
        context.update({'error_message': True})
        return render(request, 'faculty_create_group.html', {'faculty': faculty, 'course': course})
    else:
        group_create_form = GroupCreateForm()

    return render(request, 'faculty_create_group.html', {'form': group_create_form, 'faculty': faculty, 'course': course})

# Both displays groups as well as allows for the reassignment of groups


def faculty_edit_groups(request, faculty_id, course_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)
    groups = course.group_set.all()
    # get students that don't have an assigned group
    unassigned_students = course.enrolled_courses.filter(group__isnull=True)

    return render(request, 'faculty_edit_groups.html', {'faculty': faculty, 'course': course, 'groups': groups, 'unassigned_students': unassigned_students})

# Displays the information of a specific student as it pertains to the course


def faculty_student_info(request, faculty_id, course_id, student_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    course = get_object_or_404(Course, pk=course_id)
    student = get_object_or_404(Student, pk=student_id)
    group = None

    # get the student's info specific to the course here as well
    if student.group.filter(course=course).exists():
        group = student.group.get(course=course)
    preferences = Preference.objects.filter(
        student_id=student.id, group_preference__course=course).order_by('priority')

    # receive the submitted form option entry from a dropdown list
    post_data = request.POST or None
    if post_data is not None:
        context = {}
        student_group_change_form = StudentGroupChangeForm(
            course=course, data=post_data)
        if student_group_change_form.is_valid():
            student_group_change_form = student_group_change_form.cleaned_data
            # get data from the dict that the form returned
            new_group_id = student_group_change_form.get('group', "0")
            # remove student from current group in this course before adding them to new one
            student.group.remove(group)
            student.group.add(Group.objects.get(id=new_group_id))
            student.save()
            group = student.group.get(course=course)
            # reset form
            student_group_change_form = StudentGroupChangeForm(course=course)
            return render(request, 'faculty_student_info.html', {'faculty': faculty, 'course': course, 'student': student, 'group': group, 'preferences': preferences, 'form': student_group_change_form})
        else:
            print(student_group_change_form.errors.as_data())
            context.update({'error_message': True})
    else:
        student_group_change_form = StudentGroupChangeForm(course=course)

    return render(request, 'faculty_student_info.html', {'faculty': faculty, 'course': course, 'student': student, 'group': group, 'preferences': preferences, 'form': student_group_change_form})

# runs the groupsort command before returning to faculty_edit_groups


def faculty_groupsort(request, faculty_id, course_id):
    # to see line prints during execution, add "--debug" to the function arguments
   # faculty_group_sort.GroupSort(course_id, debug=True)
    call_command(course_id)
    return redirect('storyer:faculty_edit_groups', faculty_id=faculty_id, course_id=course_id)
