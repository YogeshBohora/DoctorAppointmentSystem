from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from ..models import Appointment, Appointment_Status, Notification, Reminder
from ..util import get_auth_group_name, NotificationManager as NM, STATUS
from datetime import date

def landing(request):
    print("landing")
    return render(request, 'app/landing_page.html')

def index(request):
    # return redirect('app:login')
    # return redirect('app:signup')
    return render(request, 'app/landing_page.html',{"needs_login":not request.user.is_authenticated})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_superuser:
                    return redirect('app:admin', tab='doctor')
                try:
                    doctorGroup = Group.objects.get(name='doctor')
                    doctorGroup.user_set.get(username=user.username)
                    print("app->doctor")
                    return redirect('app:index')
                except ObjectDoesNotExist:
                    print("app->index")
                    return redirect('app:index')
            else:
                return render(request, 'app/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'app/login.html', {'error_message': 'Incorrect username or password'})
    else:
        return render(request, 'app/login.html')

def logout_user(request):
    logout(request)
    return redirect('app:login')

def appointments_delete(request, pk ):
    appoint = get_object_or_404(Appointment, pk=pk)
    canceled = Appointment_Status.objects.get(status="CANCELED")
    reviewed = Appointment_Status.objects.get(status="REVIEWED")
    
    if appoint.status==canceled:
        appoint.status=reviewed
        appoint.save()
        patient_notification_config = {
            "user":appoint.patient,
            "title":"Appointment with {doc_full_name} on {visit_date} was reviewed".format(visit_date=appoint.visit_date,doc_full_name=appoint.doctor.full_name),
            "description":"Your appointment appointment booked with {doc_full_name} on {visit_date} (from {start_time} to {end_time}) was reviewed by admin".format(visit_date=appoint.visit_date, doc_full_name=appoint.doctor.full_name, start_time=appoint.start_time, end_time=appoint.end_time)
        }
        NM.create_noticication(patient_notification_config)
    else:
        appoint.status=canceled
        appoint.save()
        doctor_notification_config = {
            "user":appoint.doctor,
            "title":"Appointment with {pat_full_name} on {visit_date} was cancled".format(visit_date=appoint.visit_date, pat_full_name=appoint.patient.full_name),
            "description":"Your appointment with {pat_full_name} on {visit_date} (from {start_time} to {end_time}) was cancled".format(visit_date=appoint.visit_date, pat_full_name=appoint.patient. full_name, start_time=appoint.start_time, end_time=appoint.end_time)
        }
        patient_notification_config = {
            "user":appoint.patient,
            "title":"Appointment with {doc_full_name} on {visit_date} was canceled".format(visit_date=appoint.visit_date,doc_full_name=appoint.doctor.full_name),
            "description":"Your appointment appointment booked with {doc_full_name} on {visit_date} (from {start_time} to {end_time}) was cancled".format(visit_date=appoint.visit_date, doc_full_name=appoint.doctor.full_name, start_time=appoint.start_time, end_time=appoint.end_time)
        }
        NM.create_noticication(doctor_notification_config)
        NM.create_noticication(patient_notification_config)

    if get_auth_group_name(request) == 'doctor':
        return redirect('app:doctorappointments')
    if get_auth_group_name(request) == 'patient':
        return redirect('app:patientappointments')
    if get_auth_group_name(request) == 'administrator':
        return redirect('app:admin', tab='adminreviewappoint')

def notification_toggle_seen(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if notif.status == STATUS["SEEN"]:
        notif.status = STATUS["UNSEEN"]
    elif notif.status == STATUS["UNSEEN"]:
        notif.status = STATUS["SEEN"]
    
    notif.save()
    if get_auth_group_name(request) == 'doctor':
        return redirect('app:doctornotif')
    if get_auth_group_name(request) == 'patient':
        return redirect('app:patientnotif')
    return redirect('app:index')

def notification_delete(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    notif.status = STATUS["DELETED"]
    notif.save()
    if get_auth_group_name(request) == 'doctor':
        return redirect('app:doctornotif')
    if get_auth_group_name(request) == 'patient':
        return redirect('app:patientnotif')
    return redirect('app:index')

def disable_reminder(request):
    today = date.today()
    reminder = Reminder.objects.get(username=request.user, date=today)
    reminder.restricted = True
    reminder.save()
    return redirect('app:doctorappointments')