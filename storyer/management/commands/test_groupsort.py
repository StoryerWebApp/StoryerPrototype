'''
Docs:

custom management commands docs:
https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/

CRUD operations & working with database models/objects :
https://docs.djangoproject.com/en/4.1/intro/tutorial02/#playing-with-the-api 
'''

from django.core.management.base import BaseCommand, CommandError
from storyer.models import Student, Assignment, Group
import math

# to run: python3 manage.py test
# or py manage.py test --options

class Command(BaseCommand):
    help = 'Places students into assignment groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable console prints'
        )

    # prints out all students in db
    def handle(self, *args, **options):
        # clear all current assigned groups relationships
        for group in Group.objects.all():
            for student in group.assigned_group.all():
                student.group.remove(group)
                student.save()
            if(options['debug']):
                print(group, ": ", group.assigned_group.all())
                print()

        if options['debug']:
            print("Students:")
            for student in Student.objects.all():
                print(student)
                print(student.preference_set.all())
                print()

        # one-time access for table sizes
        numGroups = Group.objects.count()

        # calculates the min and max group size based on student to group ratio
        range = calculateGroupSizeRange()
        minGroupSize = range[0]
        maxGroupSize = range[1]
        if options['debug']:
            print("num students: ", Student.objects.count())
            print("num groups: ", Group.objects.count())
            print("min:", minGroupSize, ", max:", maxGroupSize)
            print()

        # STEP 1: fill all groups until the minimum size is reached, starting with
        # students who have that group as their priority. once one level of priority
        # has been used
        priority = 1            # incr until at last preference
        studentsInGroup = 0     # how many students currently reside in aa group
        while studentsInGroup < (numGroups * minGroupSize):
            while priority < numGroups:
                for group in Group.objects.all():
                    # the students in this group
                    group_students = group.assigned_group.all()
                    # if the group is not at min size, add students
                    if group_students.count() < minGroupSize:
                        # only check students that aren't already assigned to group
                        for student in Student.objects.filter(group__isnull=True):
                            # check student's priority, if it matches current group
                            student_preference = student.preference_set.get(priority=priority)
                            if group.id == student_preference.group_preference.id:
                                group.assigned_group.add(student)
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
            for group in Group.objects.all():
                print(group.name, ": ")
                for student in group.assigned_group.all():
                    print(student, ", priority for ", student.preference_set.get(group_preference=group))
                print()

        # STEP 2: once groups have all been ensured to have the minimum number of
        # students, now they can be filled until the rest of the students have been
        # placed in a group

        # until all students are in a group
        priority = 1
        while studentsInGroup < Student.objects.count():
            while priority < numGroups:
                for group in Group.objects.all():
                    group_students = group.assigned_group.all()
                    # as long as the group isn't at max size
                    if group_students.count() < maxGroupSize:
                        # like the same check as before, look at student priority for this group
                        # before adding
                        for student in Student.objects.filter(group__isnull=True):
                            student_preference = student.preference_set.get(priority=priority)
                            if group.id == student_preference.group_preference.id:
                                group.assigned_group.add(student)
                                studentsInGroup += 1
                                break
                        # end student search
                    # endif
                # end group loop
                priority += 1
            priority = 1
        # end student assignment

        if options['debug']:
            for group in Group.objects.all():
                print(group)
                print(group.assigned_group.all())
                print()

# calculates the min and max group size based on student to group ratio
def calculateGroupSizeRange():
    # set vars to return later
    minGroupSize, maxGroupSize = -1, -1

    # get the ratio of students to groups
    numStudents = Student.objects.count()
    numGroups = Group.objects.count()
    midSize = numStudents / numGroups

    # get 2 ints, 1 above and below ratio for max and min group size
    # if not an int
    if (numStudents % numGroups) != 0:
        #print("uneven distribution")
        minGroupSize = math.floor(midSize) - 1
        maxGroupSize = math.ceil(midSize)
    #endif
    # if the ratio of groups to students is even
    else:
        #print("even distribution")
        minGroupSize = midSize - 1
        maxGroupSize = midSize + 1
    
    return [minGroupSize, maxGroupSize]
