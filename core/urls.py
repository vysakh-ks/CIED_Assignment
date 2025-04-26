from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', LoginUserView.as_view(), name='login'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),
    path('users/', ManageUserView.as_view(), name='users'),
    path('manage_medicines/', ManageMedicinesView.as_view(), name='medicines'),
    path('billing/', BillingView.as_view(), name='billing'),
    path('dashboard/stocks/', AvailableStocksView.as_view(), name='available_stocks'),
    path('dashboard/sales_report/', SalesReportView.as_view(), name='sales_report'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
