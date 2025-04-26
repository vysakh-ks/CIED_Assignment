from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import permissions
from django.db.models import F
from .models import *
from django.db.models import Sum, Count


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and(request.user.is_superuser or request.user.user_type == 'admin'))
    
class IsInventoryManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.user_type == 'inventory_manager')
    
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.user_type == 'staff')
    
class RegisterUserView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if MedicalShopUser.objects.filter(username=request.data.get('username')).exists():
            return Response({'error': 'username already exists'}, status=400)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)

class LoginUserView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
            }
        }, status=200)
    
class LogoutUserView(APIView):
    permission_classes = [AllowAny, IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ManageUserView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = MedicalShopUser.objects.all()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user_id = request.data.get('id')
        try:
            user = MedicalShopUser.objects.get(id=user_id)
            return Response({
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'name': user.name
            }, status=200)
        except MedicalShopUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request):
        user_id = request.data.get('id')
        try:
            user = MedicalShopUser.objects.get(id=user_id)
            print(request.data)
            serializer = RegisterSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=400)
        except MedicalShopUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
    def delete(self, request):
        user_id = request.data.get('id')
        try:
            user = MedicalShopUser.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except MedicalShopUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ManageMedicinesView(APIView):
    permission_classes = [IsInventoryManager]
    def get(self, request):

        if 'medicine_id' in request.data and request.data['medicine_id']:
            medicine_id = request.data['medicine_id']
            try:
                medicine = Medicines.objects.get(id=medicine_id)
                return Response({
                    'id': medicine.id,
                    'name': medicine.name,
                    'quantity': medicine.quantity,
                    'price': medicine.price,
                    'packaging_price_multipier': medicine.packaging_price_multipier,
                    'packaging_type': medicine.packaging_type,
                    'category': medicine.category,
                    'created_by': medicine.created_by.username if medicine.created_by else None
                }, status=200)
            except Medicines.DoesNotExist:
                return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            medicines = Medicines.objects.all()
            if not medicines:
                return Response({'message': 'No medicines found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MedicineSerializer(medicines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if Medicines.objects.filter(name=request.data.get('name')).exists():
            Medicines.objects.filter(name=request.data.get('name')).update(quantity=F('quantity') + request.data.get('quantity'))
            return Response({'error': 'quantity updated for this existing medicine'}, status=400)
        
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({'message': 'Medicine added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        medicine_id = request.data.get('id')
        if not medicine_id:
            return Response({'error': 'Medicine ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            medicine = Medicines.objects.get(id=medicine_id)
            serializer = MedicineSerializer(medicine, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Medicine updated successfully'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=400)
        except Medicines.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        medicine_id = request.data.get('id')
        if not medicine_id:
            return Response({'error': 'Medicine ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            medicine = Medicines.objects.get(id=medicine_id)
            medicine.delete()
            return Response({'message': 'Medicine deleted successfully'}, status=status.HTTP_200_OK)
        except Medicines.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
        
class BillingView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        medicine_id = request.data.get('medicine_id')
        quantity = request.data.get('quantity')
        packaging_type = request.data.get('packaging_type')

        packaging_multipliers = {
            'single': 1,
            'strip': 10,
            'box': 100,
            'pack': 50,
            }

        if not medicine_id and not quantity and not packaging_type:
            return Response({'error': 'Medicine ID, quantity, and packaging type are required.'}, status=status.HTTP_400_BAD_REQUEST)
        quantity = int(quantity)

        if packaging_type not in ['single', 'strip', 'box', 'pack']:
            return Response({'error': 'Invalid packaging type'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = Medicines.objects.get(id=medicine_id)

            if medicine.quantity < quantity or quantity <= 0:
                return Response({'error': 'Insufficient quantity available'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_price = medicine.price * quantity * packaging_multipliers.get(packaging_type, 1)
            bill = Bills.objects.create(
                staff=request.user,
                medicine=medicine,
                quantity=quantity,
                packaging_type=packaging_type,
                total_price=total_price
            )
            medicine.quantity -= quantity
            medicine.save()

            return Response({
                'message': 'Bill created successfully',
                'bill_id': bill.id,
                'total_price': total_price,
                'packaging_type': packaging_type,
                'quantity': quantity,
                'medicine_name': medicine.name,
                'created_at': bill.created_at,
            }, status=status.HTTP_201_CREATED)
        
        except Medicines.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=404)


class AvailableStocksView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        medicines = Medicines.objects.all()
        if not medicines:
            return Response({'message': 'No medicines found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MedicineSerializer(medicines, many=True)
        medicines_data = [{'name': data['name'], 'quantity': data['quantity']} for data in serializer.data]
        return Response(medicines_data, status=status.HTTP_200_OK)

class SalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            billings = Bills.objects.all()
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=400)
            billings = Bills.objects.filter(created_at__range=[start_date, end_date])

        if not billings.exists():
            return Response({"error": "No billings found for the given date range."}, status=404)

        report = billings.values('staff__id', 'staff__name').annotate(
            staff_total_sales=Count('id'),
            staff_total_revenue=Sum('total_price')
        )
        total_sales = Bills.objects.aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('total_price')
        )

        return Response({
            "message": "Sales report generated successfully",
            "report": report,
            "total_sales": total_sales['total_sales'],
            "total_revenue": total_sales['total_revenue']

        })
    
