from django.db import models
from django.utils import timezone

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Visitor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=100, blank=True, null=True)
    host = models.ForeignKey(Employee, on_delete=models.CASCADE)
    purpose = models.TextField(blank=True, null=True)
    badge_id = models.CharField(max_length=20, unique=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    is_checked_in = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.badge_id}"
    
    def check_out(self):
        self.check_out_time = timezone.now()
        self.is_checked_in = False
        self.save()