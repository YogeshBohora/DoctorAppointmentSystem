from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Patient(models.Model):
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=10)
    admin_note = models.CharField(max_length=255, default="")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "user_name: {username}, , created_on: {createdOn}, updated_on: {updatedOn}".format(username=self.username, updatedOn=self.updated_on, createdOn=self.created_on)
    
    @property
    def get_created_on_date(self):
        return self.created_on.strftime("%d %b %Y")

    @property
    def get_updated_on_date(self):
        return self.updated_on.strftime("%d %b %Y")
    
    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

class Doctor(models.Model):
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=10)
    admin_note = models.CharField(max_length=255, default="")
    appointments = models.ManyToManyField(Patient, through='Appointment')
    enrolled_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "user_name: {username}, updated_on: {updatedOn}".format(username=self.username, updatedOn=self.updated_on)
    
    @property
    def get_created_on_date(self):
        return self.enrolled_on.strftime("%d %b %Y")

    @property
    def get_updated_on_date(self):
        return self.updated_on.strftime("%d %b %Y")
        
    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    
class Doctor_Specialty(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="specialty")
    specialization_in = models.CharField(max_length=40) 
    description = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "specialization in : {specializationIn}".format(specializationIn=self.specialization_in)

class Hospital_Affiliation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="affiliation")
    hospital_name = models.CharField(max_length=120)
    description = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user_name: {hospital_name}".format(hospital_name=self.hospital_name)

class Doctor_Avaliability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="avaliability")
    day_in_week = models.CharField(max_length=10)
    starting_time = models.TimeField()
    ending_time = models.TimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "user_name: {doctor}: day: {day}".format(doctor=self.doctor, day=self.day_in_week)

class Doctor_Unavaliable_Date(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user_name: {doctor}: date: {date}".format(doctor=self.doctor, date=self.date)

class Appointment_Status(models.Model):
    status = models.CharField(max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "status: {status}".format(status=self.status)


class Payment(models.Model):
    idx = models.CharField(max_length=22)
    type_idx = models.CharField(max_length=22)
    type_name = models.CharField(max_length=50)
    state_idx = models.CharField(max_length=22)
    state_name = models.CharField(max_length=50)
    amount = models.DecimalField(decimal_places=0,max_digits=10)
    created_on = models.DateTimeField()

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    status = models.ForeignKey(Appointment_Status, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    visit_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    invite_reason = models.CharField(max_length=255)

    @property
    def get_created_on_date(self):
        return self.created_on.strftime("%d %b %Y")

    @property
    def get_updated_on_date(self):
        return self.updated_on.strftime("%d %b %Y")

class Notification(models.Model):
    title = models.CharField(max_length=255) 
    description = models.CharField(max_length=255)
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "title: {title}".format(title=self.title)

class Reminder(models.Model):
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    restricted = models.BooleanField()
    date = models.DateTimeField()

    def __str__(self):
        return "reminder for {username} on {date}".format(date=self.date, username=self.username)