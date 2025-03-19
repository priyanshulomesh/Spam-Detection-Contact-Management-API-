import random
from faker import Faker
from django.contrib.auth import get_user_model
from myapp.models import Contact, UserPhoneContact, ReportDetails
from django.core.management.base import BaseCommand
# Initialize Faker
fake = Faker()

# Get the User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with test data for users, contacts, and reports'

    def handle(self, *args, **kwargs):
        print("Running random data population")
        # Clear existing data
        print("Deleting existing users")
        User.objects.all().delete()
        print("Deleting existing contacts")
        Contact.objects.all().delete()
        print("Deleting existing user_phone_contacts")
        UserPhoneContact.objects.all().delete()
        print("Deleting existing report_details")
        ReportDetails.objects.all().delete()

        print("Populating users")
        # Create Users
        users = []
        for _ in range(50):
            phone_number = fake.unique.random_number(digits=10, fix_len=True)
            contact = Contact.objects.create(number=phone_number)
            try:
                user = User.objects.create_user(
                    username=fake.user_name(),
                    email=fake.email(),
                    full_name=fake.name(),
                    password="password123",
                    primary_contact=contact
                )
                users.append(user)
            except:
                pass
            
        # Create additional contacts not linked to users
        print("Populating contacts")
        contacts = []
        for _ in range(100):
            try:
                contact = Contact.objects.create(number=fake.unique.random_number(digits=10, fix_len=True))
                contacts.append(contact)
            except:
                pass

        print("Populating user_phone_contacts")
        # Create UserPhoneContact relationships
        for user in users:
            for _ in range(random.randint(1, 5)):  # Each user has 1-5 personal contacts
                try:
                    contact = random.choice(contacts)
                    alias = fake.first_name()
                    UserPhoneContact.objects.get_or_create(app_user=user, phone_contact=contact, alias=alias)
                except:
                    pass

        print("Populating reports")
        # Create spam reports
        for _ in range(150):  # Randomly mark 150 contacts as spam
            try:
                user = random.choice(users)
                contact = random.choice(contacts)
                ReportDetails.objects.get_or_create(reporter=user, phone_contact=contact)
            except:
                pass

        print("Data population complete!")
