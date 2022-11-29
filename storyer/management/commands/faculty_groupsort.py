'''
Docs:

custom management commands docs:
https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/

CRUD operations & working with database models/objects :
https://docs.djangoproject.com/en/4.1/intro/tutorial02/#playing-with-the-api 
'''

from django.core.management.base import BaseCommand, CommandError
from storyer.models import Student, Assignment, Group, Course, Preference
import math

# to run: python3 manage.py test
# or py manage.py test --options

class Command(BaseCommand):
    help = 'Places students into assignment groups'

    def add_arguments(self, parser):
        parser.add_argument(
            'course_id', 
            nargs=1, 
            type=int, 
            help='ID of the course to sort'
        )

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable console prints'
        )

    # prints out all students in db
    def handle(self, *args, **options):
        course_id = int(options['course_id'][0])
        
        course = Course.objects.get(id=course_id)
        groups = course.group_set.all()
        students = course.enrolled_courses.all()

        if options['debug']:
            print("Students:")
            for student in students:
                print(student)
                print(student.preference_set.filter(group_preference__course=course).order_by('priority'))
                print()

        # one-time access for table sizes
        numStudents = students.count()
        numGroups = groups.count()

        # calculates the min and max group size based on student to group ratio
        range = calculateGroupSizeRange(numStudents, numGroups)
        minGroupSize = range[0]
        maxGroupSize = range[1]
        if options['debug']:
            print("num students: ", numStudents)
            print("num groups: ", numGroups)
            print("min:", minGroupSize, ", max:", maxGroupSize)
            print()

        # STEP 1: fill all groups until the minimum size is reached, starting with
        # students who have that group as their priority. once one level of priority
        # has been used
        priority = 1            # incr until at last preference
        studentsInGroup = 0
        for group in groups:
            studentsInGroup += group.assigned_group.count()
        while studentsInGroup < (numGroups * minGroupSize):
            while priority < numGroups:
                for group in groups:
                    # the students in this group
                    group_students = group.assigned_group.all()
                    # if the group is not at min size, add students
                    if group_students.count() < minGroupSize:
                        print("Group ", group.name, " is not full")
                        # only check students that aren't already assigned to group
                        for student in students:
                            if not student.group.filter(course=course).exists():
                                # check student's priority, if it matches current group
                                student_preference = Preference.objects.get(student_id=student.id, group_preference__course=course, priority=priority)

                                if group.id == student_preference.group_preference.id:
                                    group.assigned_group.add(student)
                                    group.save()
                                    studentsInGroup += 1
                                # if the group is now at min size, skip adding students
                                if group_students.count() == minGroupSize:
                                    break
                        # end student search to add loop
                # end group loop
                # check group sizes to see if can break loop
                priority += 1
            # end incr prefer-index
        # end filling groups

        if options['debug']:
            print("after part 1:")
            for group in groups:
                print(group.name, ": ")
                for student in group.assigned_group.all():
                    print(student, ", priority for ", student.preference_set.get(group_preference=group))
                print()
            print("num students in groups: ", studentsInGroup, "/", numStudents)

        # STEP 2: once groups have all been ensured to have the minimum number of
        # students, now they can be filled until the rest of the students have been
        # placed in a group

        # until all students are in a group
        priority = 1
        while studentsInGroup < numStudents:
            while priority < numGroups:
                for group in groups:
                    group_students = group.assigned_group.all()
                    # as long as the group isn't at max size
                    if group_students.count() < maxGroupSize:
                        # like the same check as before, look at student priority for this group
                        # before adding
                        for student in students:
                            if not student.group.filter(course=course).exists():
                                student_preference = Preference.objects.get(student_id=student.id, group_preference__course=course, priority=priority)

                                if group.id == student_preference.group_preference.id:
                                    group.assigned_group.add(student)
                                    group.save()
                                    studentsInGroup += 1
                                    break
                        # end student search
                    # endif
                # end group loop
                priority += 1
        # end student assignment

        if options['debug']:
            for group in groups:
                print(group)
                print(group.assigned_group.all())
                print()

# calculates the min and max group size based on student to group ratio
def calculateGroupSizeRange(numStudents, numGroups):
    # set vars to return later
    minGroupSize, maxGroupSize = -1, -1

    # get the ratio of students to groups
    midSize = numStudents / numGroups

    # get 2 ints, 1 above and below ratio for max and min group size
    # if not an int
    if (numStudents % numGroups) != 0:
        minGroupSize = int(math.floor(midSize) - 1)
        maxGroupSize = int(math.ceil(midSize))
    #endif
    # if the ratio of groups to students is even
    else:
        minGroupSize = midSize - 1
        maxGroupSize = midSize + 1
    # ensure min group size is not 0 afterwards
    if minGroupSize <= 0:
        minGroupSize = 1
    return [minGroupSize, maxGroupSize]
