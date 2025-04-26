from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class MedicalShopUser(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('inventory_manager', 'Inventory Manager'),
        ('staff', 'Staff'),
    )
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Medicines(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0.0)
    date_added = models.DateTimeField(auto_now_add=True)
    # packaging_price_multipier = models.IntegerField(default=1)
    # PACKAGING_CHOICES = (
    #     ('single', 'Single'),
    #     ('strip', 'Strip'),
    #     ('box', 'Box'),
    #     ('pack', 'Pack'),
    # )
    # packaging_type = models.CharField(choices=PACKAGING_CHOICES, max_length=50)
    CATEGORIES_CHOICES = (
        ('tablet','Tablet'),
        ('capsule','Capsule'),
        ('syrup','Syrup'),
        ('injection','Injection'),
        ('ointment','Ointment'),
        ('cream','Cream'),
        ('drop','Drop'),
        ('inhalers','Inhalers'),
    )
    category = models.CharField(choices=CATEGORIES_CHOICES,max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(MedicalShopUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Medicines'

class Bills(models.Model):
    staff = models.ForeignKey(MedicalShopUser, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    packaging_type = models.CharField(max_length=50)
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Bills'

    
# class SalesReports(models.Model):
#     created_by = models.ForeignKey(MedicalShopUser, on_delete=models.CASCADE)
#     medicine = models.ForeignKey(Medicines, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     total_price = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name_plural = 'Sales Reports'