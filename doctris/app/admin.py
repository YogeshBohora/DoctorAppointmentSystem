from django.contrib import admin
from .models import Patient, Doctor, Doctor_Avaliability, Doctor_Specialty, Doctor_Unavaliable_Date, Appointment_Status, Appointment

# Register your models here.
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Doctor_Avaliability)
admin.site.register(Doctor_Specialty)
admin.site.register(Doctor_Unavaliable_Date)
admin.site.register(Appointment_Status)
admin.site.register(Appointment)
