from django.urls import path
from .views import RegisterAPIView, LoginAPIView, SearchContactByNumberAPIView,SearchContactByNameAPIView,ReportNumberAPIView,GetContactDetailsAPIView,home

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('search_by_number/', SearchContactByNumberAPIView.as_view(),name='search_by_number'),
    path('search_by_name/', SearchContactByNameAPIView.as_view(),name='search_by_name'),
    path('report_number/',ReportNumberAPIView.as_view(),name='report_number'),
    path('get_contact_details/',GetContactDetailsAPIView.as_view(),name='contact_details'),
    path('', home, name='home'),
]
