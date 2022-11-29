'''
Docs:

custom management commands docs:
https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/

CRUD operations & working with database models/objects :
https://docs.djangoproject.com/en/4.1/intro/tutorial02/#playing-with-the-api 
'''

from django.core.management.base import BaseCommand, CommandError
from storyer.models import Student, Assignment, Group, Preference
from random import shuffle

# to run: python3 manage.py test
# or py manage.py test


class Command(BaseCommand):
    help = 'Will clear DB and then add test entries to DB'

    
    def add_arguments(self, parser):
        parser.add_argument(
            'num_groups', 
            nargs=1, 
            type=int, 
            help='Number of groups to create'
        )

        parser.add_argument(
            'num_students', 
            nargs=1, 
            type=int,
            help='Number of students to create'
        )

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable console prints'
        )

    # sets up DB for Student and Group tables
    # TODO: acommodate for just adding to preexisting tables, new groups or students
    def handle(self, *args, **options):
        # delete tables by default
        Student.objects.all().delete()
        Group.objects.all().delete()
        
        if options['debug']:
            print("DB status on startup:")
            print("Groups: ", Group.objects.all())
            print("Students: ", Student.objects.all())
            print()
        
        Student.objects.all().delete()
        Group.objects.all().delete()

        # get the arg vals and set to ints
        num_groups = int(options['num_groups'][0])
        num_students = int(options['num_students'][0])

        total_groups = Group.objects.count() + num_groups
        total_students = Student.objects.count() + num_students

        for i in range(Group.objects.count(), total_groups):
            name = "test-group" + str(i+1)
            Group.objects.create(name=name)

        # begin adding students first
        for i in range(Student.objects.count(), total_students):
            name = "test" + str(i+1)
            email = "test" + str(i+1)
            password = "test" + str(i+1)
            student = Student(name=name, email=email, password=password)
            student.save()

            # create random preferences
            preferences = list(Group.objects.values_list('id', flat=True))
            shuffle(preferences)

            priority = 1
            for id in preferences:
                curr_preference = Group.objects.get(pk=id)
                student.preferences.add(curr_preference, through_defaults={'priority':priority})
                priority+=1

            student.save()

        if options['debug']:
            print("DB status after initial add:")
            print("Groups: ", Group.objects.all())
            for student in Student.objects.all():
                print("Student: ", student)
                print("Preferences: ", Preference.objects.filter(student=student))
                print()
