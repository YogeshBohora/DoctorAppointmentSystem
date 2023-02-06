from django.contrib.auth.models import User, Group
from app.models import Doctor, Patient, Notification, Doctor_Specialty, Hospital_Affiliation, Doctor_Avaliability, Doctor_Unavaliable_Date, Appointment, Appointment_Status
from django.shortcuts import get_object_or_404
import datetime as dt

def get_user_group_name(user):
    if not user.is_authenticated:
        return "anonynomous"
    return user.groups.all()[0].name

def get_auth_group_name(request):
    return get_user_group_name(request.user)

STATUS={
    "UNSEEN":"UNSEEN",
    "SEEN":"SEEN",
    "DELETED":"DELETED",
}
class NotificationManager:
    
    @staticmethod
    def create_noticication(config):
        new_notification = Notification(title=config["title"], description=config["description"], username= config["user"].username, status= STATUS["UNSEEN"] )
        new_notification.save()
        return new_notification
    
    @staticmethod
    def seen_noticication(pk):
        notif = Notification.objects.get(pk=pk)
        notif.status = STATUS['SEEN']
        notif.save()
        return notif
    
    @staticmethod
    def delete_noticication(pk):
        notif = Notification.objects.get(pk=pk)
        notif.status = STATUS['DELETED']
        notif.save()
        return notif

class Database_Accessor:

    @staticmethod
    def doctor_specialty(doc):
        return doc.specialty.all()
    
    @staticmethod
    def doctor_avaliability(doc):
        return doc.avaliability.all()
    
    @staticmethod
    def doctor_affilation(doc):
        return doc.affiliation.all()
    
    @staticmethod
    def doctor_appointments_record(doc, excludeOthers=True):
        appointments = Appointment.objects.filter(doctor=doc)
        if excludeOthers:
            canceled = Appointment_Status.objects.get(status='CANCELED')
            reviewed = Appointment_Status.objects.get(status='REVIEWED')
            return appointments.exclude(status=canceled).exclude(status=reviewed)
        else:
            return appointments
    
    @staticmethod
    def label_reminders(appointments):
        complete = Appointment_Status.objects.get(status='COMPLETE')
        canceled = Appointment_Status.objects.get(status='CANCELED')
        reviewed = Appointment_Status.objects.get(status='REVIEWED')
        upcomming = []
        past = []
        todays = []
        after_one_day = []
        after_two_days = []
        today = dt.date.today()
        for appoint in appointments.exclude(status=canceled).exclude(status=reviewed):
            if appoint.status==complete:
                past.append(appoint)
            else:
                if today == appoint.visit_date: 
                    todays.append(appoint)
                elif today < appoint.visit_date:
                    upcomming.append(appoint)
                    if (appoint.visit_date == today+dt.timedelta(days=1)):
                        after_one_day.append(appoint)
                    elif (appoint.visit_date == today+dt.timedelta(days=2)):
                        after_two_days.append(appoint)
                else:
                    past.append(appoint)
        
        return {
                "past": past,
                "today": todays,
                "after_one_day": after_one_day,
                "after_two_days": after_two_days,
                "upcomming": upcomming,
                "canceled": appointments.filter(status=canceled),
                "reviewed": appointments.filter(status=reviewed),
            }

    @staticmethod
    def label_appointments(appointments):
        complete = Appointment_Status.objects.get(status='COMPLETE')
        canceled = Appointment_Status.objects.get(status='CANCELED')
        reviewed = Appointment_Status.objects.get(status='REVIEWED')
        upcomming = []
        past = []
        todays = []
        today = dt.date.today()
        for appoint in appointments.exclude(status=canceled).exclude(status=reviewed):
            if appoint.status==complete:
                past.append(appoint)
            else:
                if today == appoint.visit_date:
                    todays.append(appoint)
                elif today < appoint.visit_date:
                    upcomming.append(appoint)
                else:
                    past.append(appoint)
        
        return {
                "past": past,
                "todays": todays,
                "upcomming": upcomming,
                "canceled": appointments.filter(status=canceled),
                "reviewed": appointments.filter(status=reviewed),
            }

    @staticmethod
    def patient_appointments_record(pat, excludeOthers=True):
        appointments = Appointment.objects.filter(patient=pat)
        if excludeOthers:
            canceled = Appointment_Status.objects.get(status='CANCELED')
            reviewed = Appointment_Status.objects.get(status='REVIEWED')
            return appointments.exclude(status=canceled).exclude(status=reviewed)
        else:
            return appointments
    
    

    @staticmethod
    def check_user_password(username, password):
        return get_object_or_404(User, username=username).check_password(password)
    
    @staticmethod
    def update_entry(entry, value, keys):
        if 'first_name' in keys:
            entry.first_name = value['first_name']
        if 'last_name' in keys:
            entry.last_name = value['last_name']
        if 'email' in keys:
            entry.email = value['email']
        if 'phone' in keys:
            entry.phone = value['phone']
        if 'visit_date' in keys:
            entry.visit_date = value['visit_date']
        if 'start_time' in keys:
            entry.start_time = value['start_time']
        if 'end_time' in keys:
            entry.end_time = value['end_time']
        if 'invite_reason' in keys:
            entry.invite_reason = value['invite_reason']
        if 'day_in_week' in keys:
            entry.day_in_week = value['day_in_week']

        if 'starting_time' in keys:
            entry.starting_time = value['starting_time']
        if 'ending_time' in keys:
            entry.ending_time = value['ending_time']
            
        if 'hospital_name' in keys:
            entry.hospital_name = value['hospital_name']
        if 'description' in keys:
            entry.description = value['description']
        if 'city' in keys:
            entry.city = value['city']
        if 'country' in keys:
            entry.country = value['country']
        if 'specialization_in' in keys:
            entry.specialization_in = value['specialization_in']
        if 'username' in keys:
            entry.username = value['username']
        return entry

def compare_weekday(week_int, week_char):
    if week_int == 0 and week_char == "Monday":
        print(week_int, week_char)
        return True
    elif week_int == 1 and (week_char == "Tuesday" or week_char == "Tueday"):
        print(week_int, week_char)
        return True
    elif week_int == 2 and week_char == "Wednesday":
        print(week_int, week_char)
        return True
    elif week_int == 3 and week_char == "Thursday":
        print(week_int, week_char)
        return True
    elif week_int == 4 and week_char == "Friday":
        print(week_int, week_char)
        return True
    elif week_int == 5 and week_char == "Saturday":
        print(week_int, week_char)
        return True
    elif week_int == 6 and week_char == "Sunday":
        print(week_int, week_char)
        return True
    else:
        print("false", week_int, week_char)
        return False

