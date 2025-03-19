from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from myapp.models import Contact, UserPhoneContact, ReportDetails
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db.models import Count, Q

User = get_user_model()

@api_view(['GET'])
def home(request):
    return Response({"message": "Welcome to the Home Page"}, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract user registration data
        full_name = request.data.get("full_name")
        email = request.data.get("email")
        password = request.data.get("password")
        phone_number = request.data.get("number")

        # Validate required fields
        if not (full_name and password and phone_number):
            return Response({"error": "Full name, password and phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the phone number is already taken
        if phone_number and User.objects.filter(primary_contact__number=phone_number).exists():
            return Response({"error": "User with this phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Hash the password before storing it
        hashed_password = make_password(password)

        try:
            # Manually create Contact instance
            phone_contact, created = Contact.objects.get_or_create(number=phone_number)

            # Manually create the User instance
            user = User.objects.create(
                full_name=full_name,
                email=email,
                password=hashed_password,
                primary_contact=phone_contact
            )

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "User registered successfully.",
                "access_token": access_token,
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Check if user is already authenticated
        if request.user.is_authenticated:
            home_url = reverse('home')  # Replace 'home' with your home route name
            return Response({"redirect": home_url}, status=status.HTTP_302_FOUND)
        
        password = request.data.get("password")
        phone_number = request.data.get("number")

        if not phone_number or not password:
            return Response({"error": "Phone number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(primary_contact__number=phone_number)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")

        if not check_password(password, user.password):
            raise AuthenticationFailed("Invalid email or password.")

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
    

class SearchContactByNumberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phone_number = request.query_params.get("number")
        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        results = {}
        try:
            search=User.objects.get(primary_contact__number=phone_number)
            results["names"] = [
                {
                    "id": search.id,
                    "name": search.full_name,
                    "is_registered": 1
                }
            ]
        except User.DoesNotExist:
            search = UserPhoneContact.objects.filter(phone_contact__number=phone_number)
            results["names"] = [
                {
                    "id": s.id,
                    "name": s.alias,
                    "is_registered": 0
                } for s in search]
            
        spam_count = ReportDetails.objects.filter(phone_contact__number=phone_number).count()

        results["spam_count"] = spam_count
        return Response(results, status=status.HTTP_200_OK)
    
class SearchContactByNameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response({"error": "Name is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        search=[]
        # First append the names starting with
        user_starts_with = (
            User.objects.filter(full_name__startswith=name)
            .annotate(
                number=models.F("primary_contact__number"),
                spam_count=Count("primary_contact__reportdetails"),
            )
            .values("full_name", "number", "spam_count")
        )

        search.extend(
            [
                {
                    "id": obj.get(id),
                    "full_name": obj.get("full_name"),
                    "number": obj.get("number"),
                    "spam_count": obj.get("spam_count"),
                    "is_registered": 1
                } for obj in user_starts_with
            ]
        )

        others_starts_with = (
            UserPhoneContact.objects.filter(alias__startswith=name)
            .annotate(
                number=models.F("phone_contact__number"),
                spam_count=Count("phone_contact__reportdetails")
            )
            .values("alias", "number", "spam_count")
        )
        search.extend(
            [
                {
                    "id": obj.get(id),
                    "full_name": obj.get('alias'),
                    "number": obj.get('number'),
                    "spam_count": obj.get('spam_count'),
                    "is_registered": 0
                } for obj in others_starts_with
            ]
        )

        # Now append the name containing
        user_contains = (
            User.objects.filter(
                Q(full_name__contains=name) & ~Q(full_name__startswith=name)
            )
            .annotate(
                number=models.F("primary_contact__number"),
                spam_count=Count("primary_contact__reportdetails"),
            )
            .values("full_name", "number", "spam_count")
        )

        search.extend(
            [
                {
                    "id": obj.get(id),
                    "full_name": obj.get("full_name"),
                    "number": obj.get("number"),
                    "spam_count": obj.get("spam_count"),
                    "is_registered": 1
                } for obj in user_contains
            ]
        )

        others_contains = (
            UserPhoneContact.objects.filter(
                Q(alias__contains=name) & ~Q(alias__startswith=name)
            )
            .annotate(
                number=models.F("phone_contact__number"),
                spam_count=Count("phone_contact__reportdetails")
            )
            .values("alias", "number", "spam_count")
        )

        search.extend(
            [
                {
                    "id": obj.get(id),
                    "full_name": obj.get('alias'),
                    "number": obj.get('number'),
                    "spam_count": obj.get('spam_count'),
                    "is_registered": 0
                } for obj in others_contains
            ]
        )
        return Response({"results": search}, status=status.HTTP_200_OK)


class ReportNumberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number=request.data.get("number")

        contact,created=Contact.objects.get_or_create(number=phone_number)

        user=request.user

        reportDetails, report_detail_created=ReportDetails.objects.get_or_create(phone_contact=contact,reporter=user)

        if not report_detail_created:
            return Response(
                {"message": "You have already reported this contact."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message":"Contact reported successfully"},status=status.HTTP_201_CREATED)

class GetContactDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        id=request.query_params.get("id")
        is_registered=request.query_params.get("is_registered")
        print(user.id)
        if is_registered:
            try:
                contact_user = User.objects.get(id=id)
                phone_number = contact_user.primary_contact.number
                response = {
                    "id": id,
                    "full_name": contact_user.full_name,
                    "phone_number": phone_number,
                    "spam_count": ReportDetails.objects.filter(phone_contact__number=phone_number).count(),
                    "is_registered": 1
                }
                if UserPhoneContact.objects.filter(
                    Q(app_user=contact_user) & Q(phone_contact=user.primary_contact)
                ).exists():
                    response["email"] = contact_user.email
            except User.DoesNotExist:
                return Response({"message": "User Not Found"},status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                contact_user = UserPhoneContact.objects.get(id=id)
                phone_number = contact_user.phone_contact.number
                response = {
                    "id": id,
                    "full_name": contact_user.alias,
                    "phone_number": phone_number,
                    "spam_count": ReportDetails.objects.filter(phone_contact__number=phone_number).count(),
                    "is_registered": 0
                }
            except User.DoesNotExist:
                return Response({"message": "User Not Found"},status=status.HTTP_404_NOT_FOUND)

        return Response(response,status=status.HTTP_200_OK)




