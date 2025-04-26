from rest_framework import serializers
from .models import MedicalShopUser, Medicines, Bills

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalShopUser
        fields = ['id', 'username', 'email', 'password', 'user_type', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MedicalShopUser.objects.create_user(**validated_data)
        return user

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicines
        fields = '__all__'

    def create(self, validated_data):
        medicine = Medicines.objects.create(**validated_data)
        return medicine
    
class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bills
        fields = '__all__'


