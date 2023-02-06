from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.contrib.auth import login, authenticate
from django.shortcuts import render, get_object_or_404, redirect
from ..util import get_auth_group_name, compare_weekday, Database_Accessor as DA, NotificationManager as NM, STATUS
from ..models import Doctor, Patient, Doctor_Specialty, Hospital_Affiliation, Doctor_Avaliability, Doctor_Unavaliable_Date, Appointment, Appointment_Status, Notification, Reminder
from ..forms import DoctorForm, UserForm
from datetime import datetime
import datetime as dt

def doctor(request):
    doctor = get_object_or_404(Doctor, username=request.user)
    context = {
        "needs_login":False, 
        "doctor":doctor, 
        "specializations": DA.doctor_specialty(doctor), 
        "hospitals": DA.doctor_affilation(doctor), 
        "avaliability": DA.doctor_avaliability(doctor)
    }
    return render(request, 'app/doctor_profile_page.html',context)

def doctor_edit_info(request):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = 'app/doctor_profile_edit.html'
    context = {
        "needs_login":False,
        "obj":doctor,
    }
    if request.method == "POST":
        password = request.POST['password']
        doctor = DA.update_entry(doctor, request.POST, ['first_name','last_name','email','phone'])
        if DA.check_user_password(request.user,password):
            doctor.save()
            context.update({"success":True})
        else:
            context.update({"password_invalid":True})
    return render(request, template_name, context)

def doctor_edit_cred(request):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = "app/doctor_profile_edit_cred.html"
    context = {
        "needs_login":False, 
        "obj":doctor,
    }
    if request.method == "POST":
        docuser = get_object_or_404(User, username=request.user)
        if DA.check_user_password(request.user, request.POST['old_password']):
            if request.POST['new_password'] == request.POST['confirm_password']:
                docuser = DA.update_entry(docuser, request.POST, ['username'])
                docuser.set_password(request.POST['new_password'])
                doctor.username = docuser
                try:
                    docuser.save()
                    doctor.save()
                    user = authenticate(username=docuser.username, password=request.POST['new_password'])
                    login(request, user)
                    return redirect('app:login')
                except IntegrityError:
                    context.update({"user_error":True})
            else:
                context.update({"confirm_invalid":True})
        else:
            context.update({"password_invalid":True})
    return render(request, template_name, context)

def doctor_delete_relation(request, rel_name, pk ):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = 'app/doctor_profile_edit.html'
    context = {
        "needs_login":False,
        "obj": doctor,
        "success":True
    }
    if rel_name == 'avaliability':
        avail = Doctor_Avaliability.objects.get(pk=pk)
        avail.delete()
    if rel_name == 'speciality':
        speciality = Doctor_Specialty.objects.get(pk=pk)
        speciality.delete()
    if rel_name == 'affiliations':
        affiliation = Hospital_Affiliation.objects.get(pk=pk)
        affiliation.delete()
    return render(request, template_name, context)

def doctor_spec_relation(request, pk ):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = 'app/doctor_profile_edit_spec.html'
    context = {
        "needs_login":False,
    }
    if request.method == "POST":
        if pk == '-1':
            newSpeciality = Doctor_Specialty(doctor=doctor, specialization_in=request.POST["specialization_in"], description=request.POST["description"])
            newSpeciality.save()
            context.update({'success':True})
        else:
            speciality = get_object_or_404(Doctor_Specialty, pk=pk)
            speciality = get_object_or_404(Doctor_Specialty, pk=pk)
            speciality = DA.update_entry(speciality, request.POST, ["specialization_in","description"])
            speciality.save()
            context.update({'success':True})
    else:
        if pk != '-1':
            speciality = get_object_or_404(Doctor_Specialty, pk=pk)
            context.update({'obj': speciality, 'as_edit': True})
    return render(request, template_name, context)


def doctor_aff_relation(request, pk ):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = 'app/doctor_profile_edit_aff.html'
    context = {
        "needs_login":False,
    }
    if request.method == "POST":
        if pk == '-1':
            newAffiliation = Hospital_Affiliation(doctor=doctor, hospital_name=request.POST["hospital_name"], description=request.POST["description"], city=request.POST["city"], country=request.POST["country"])
            newAffiliation.save()
            context.update({'success':True})
        else:
            affiliation = Hospital_Affiliation.objects.get(pk=pk)
            affiliation = DA.update_entry(affiliation, request.POST, ["hospital_name","description","city","country"])
            affiliation.save()
            context.update({'success':True})
    else:
        if pk != '-1':
            affiliation = Hospital_Affiliation.objects.get(pk=pk)
            context.update({'obj': affiliation, 'as_edit': True})
    return render(request, template_name, context)

def doctor_avail_relation(request, pk ):
    doctor = get_object_or_404(Doctor, username=request.user)
    template_name = 'app/doctor_profile_edit_avail.html'
    context = {
        "needs_login":False,
    }
    if request.method == "POST":
        starttime_object = datetime.strptime(request.POST["starting_time"], "%H:%M")
        endtime_object = datetime.strptime(request.POST["ending_time"], "%H:%M")
        if starttime_object >= endtime_object:
            context.update({"invalid_date":True})
        else:
            if pk == '-1':
                newAvail = Doctor_Avaliability(doctor=doctor, day_in_week=request.POST["day_in_week"],starting_time=request.POST["starting_time"], ending_time=request.POST["ending_time"])
                newAvail.save()
                context.update({"success":True})
            else:
                avail = Doctor_Avaliability.objects.get(pk=pk)
                avail = DA.update_entry(avail, request.POST, ['day_in_week',"starting_time","ending_time"])
                avail.save()
                context.update({"success":True})
    else:
        if pk != '-1':
            avail = Doctor_Avaliability.objects.get(pk=pk)
            avail.starting_time = avail.starting_time.strftime("%H:%M")
            avail.ending_time = avail.ending_time.strftime("%H:%M")
            context.update({"obj":avail, "as_edit":True})
    return render(request, template_name, context)

def doctor_appointment_edit(request, pk ):
    today = dt.date.today().strftime("%Y-%m-%d")
    doctor = get_object_or_404(Doctor, username=request.user)
    appointment_to_edit =  get_object_or_404(Appointment, pk=pk)
    specializations, hospitals, avaliability, appointments = [ 
        DA.doctor_specialty(doctor), 
        DA.doctor_affilation(doctor), 
        DA.doctor_avaliability(doctor), 
        DA.doctor_appointments_record(doctor)
    ]

    appointment_to_edit.visit_date = appointment_to_edit.visit_date.strftime("%Y-%m-%d")
    appointment_to_edit.start_time = appointment_to_edit.start_time.strftime("%H:%M")
    appointment_to_edit.end_time = appointment_to_edit.end_time.strftime("%H:%M")

    template_name='app/doctor_appointment_edit.html'
    context={
        "needs_login":False,
        "doctor":doctor, 
        "specializations":specializations, 
        "hospitals":hospitals, 
        "avaliability":avaliability, 
        "appointments":appointments, 
        "today_date":today, 
        "as_edit":True,
    }

    if request.method == "POST":
        visit_date = request.POST['visit_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        invite_reason = request.POST['invite_reason']
        visit_date_object = datetime.strptime(visit_date, "%Y-%m-%d")
        starttime_object = datetime.strptime(start_time, "%H:%M")
        endtime_object = datetime.strptime(end_time, "%H:%M")

        if starttime_object >= endtime_object:
            context.update({'invalid_time': True})
        # check if start time and end time  is avaliable for doctor
        # step 1check if the visit date is in avaliableweekday
        else:
            is_weekday_avail = False
            doc_avail_weekday = []
            for avail in avaliability:
                if compare_weekday( visit_date_object.weekday(),  avail.day_in_week):
                    is_weekday_avail = True
                    doc_avail_weekday.append(avail)
            if not is_weekday_avail:
                context.update({ "invalid_weekday": True })
            else:
                if is_weekday_avail:
                    is_time_avaliable = False
                    doc_avail_weekday_time = []
                    # check if the appointment time falls in general avaliable time for the day
                    for avail in doc_avail_weekday:
                        if avail.starting_time <= starttime_object.time() and avail.ending_time >= endtime_object.time() :
                            is_time_avaliable = True
                            doc_avail_weekday_time.append(avail)
                    if not is_time_avaliable:
                        context.update({ "invalid_appointment_time": True })
                    else:
                        #now checking if the starttime and end time of new appointment conflicts with any other appointment the doctor has that day  
                        all_appointments_for_doc = Appointment.objects.filter(doctor=doctor, visit_date=visit_date_object.date())
                        has_appointment_collision = False
                        for appoint in all_appointments_for_doc:
                            if(appoint.start_time < starttime_object.time() and appoint.end_time > starttime_object.time()) or (appoint.start_time < endtime_object.time() and appoint.end_time > endtime_object.time()):
                                has_appointment_collision = True
                        if has_appointment_collision:
                            context.update({ "has_appointment_collision": True })
                        else:
                            patient_notification_config = {
                                "user":appointment_to_edit.patient,
                                "title":"{doc_name} updated appointment of {prev_visit_date}".format(prev_visit_date=appointment_to_edit.visit_date, doc_name=appointment_to_edit.doctor.full_name),
                                "description":"{doc_name} updated appointment of date {prev_visit_date} ( from {prev_start_time} - {prev_end_time} ) to date {visit_date} ( from {start_time} - {end_time} )".format(doc_name=appointment_to_edit.doctor.full_name, prev_visit_date=appointment_to_edit.visit_date, prev_start_time=appointment_to_edit.start_time, prev_end_time=appointment_to_edit.end_time, visit_date=visit_date, start_time=start_time, end_time=end_time )
                            }
                            doctor_notification_config = {
                                "user":appointment_to_edit.doctor,
                                "title":"You have successfully updated appointment of {prev_visit_date} with {pat_name}".format(prev_visit_date=appointment_to_edit.visit_date, pat_name=appointment_to_edit.patient.full_name),
                                "description":"Your appointment with {pat_name} of date {prev_visit_date} (from {prev_start_time} - {prev_end_time}) has been successfully updated to date {visit_date} (from {start_time} - {end_time})".format(pat_name=appointment_to_edit.doctor.full_name, prev_visit_date=appointment_to_edit.visit_date, prev_start_time=appointment_to_edit.start_time, prev_end_time=appointment_to_edit.end_time, visit_date=visit_date, start_time=start_time, end_time=end_time )
                            }
                            print(doctor_notification_config)
                            print(patient_notification_config)
                            # edit the appointment
                            # incomplete_status = Appointment_Status.objects.get(status="INCOMPLETE")
                            updateData = {
                                "visit_date":visit_date_object.date(),
                                "start_time":start_time,
                                "end_time":end_time,
                                "invite_reason":invite_reason,
                            }
                            appointment_to_edit = DA.update_entry(appointment_to_edit, updateData, ["visit_date", "start_time", "end_time", "invite_reason"])
                            appointment_to_edit.save()
                            NM.create_noticication(doctor_notification_config)
                            NM.create_noticication(patient_notification_config)
                            try:
                                today = dt.date.today()
                                reminder = Reminder.objects.get(username=appointment_to_edit.patient.username, date=today)
                                reminder.restricted=False
                                reminder.save()
                            except:
                                new_reminder = Reminder(username=appointment_to_edit.patient.username, restricted=False, date=today)
                                new_reminder.save()
                            context.update({"success":True})
    # for get requests
    context.update({"obj":appointment_to_edit})
    return render(request, template_name,context)

def doctor_appointments_view(request ):
    doctor = get_object_or_404(Doctor, username=request.user)
    appointments = DA.doctor_appointments_record(doctor)
    labeled_appointments = DA.label_appointments(appointments)
    context= {
        "needs_login":False,
        "upcomming_appointments": labeled_appointments["upcomming"],
        "past_appointments": labeled_appointments["past"],
        "todays_appointments": labeled_appointments["todays"],
    }
    return render(request, 'app/doctor_appointments_view.html',context)

def doctor_appointments_view_reminder(request):
    doctor = get_object_or_404(Doctor, username=request.user)
    appointments = DA.doctor_appointments_record(doctor)
    labeled_reminders = DA.label_reminders(appointments)
    notifications = Notification.objects.filter(username=request.user.username, status=STATUS["UNSEEN"])
    print(labeled_reminders)
    if (not notifications) and (not labeled_reminders["today"] and not labeled_reminders["upcomming"]):
        return redirect('app:disablereminder')

    context= {
        "needs_login":False,
        "upcomming_appointments": labeled_reminders["upcomming"],
        "past_appointments": labeled_reminders["past"],
        "notifications": notifications,
        "today": labeled_reminders["today"],
        "after_one_day": labeled_reminders["after_one_day"],
        "after_two_days": labeled_reminders["after_two_days"],
        "notifications_count":notifications.count()
    }
    return render(request, 'app/doctor_reminder_page.html',context)

def doctor_notifications_view(request):
    doctor = get_object_or_404(Doctor, username=request.user)
    notifications = Notification.objects.filter(username=doctor.username)
    seen = notifications.filter(status=STATUS["SEEN"])
    unseen = notifications.filter(status=STATUS["UNSEEN"])
    context={
        "needs_login":False,
        "seen":seen,
        "unseen":unseen,
    }
    return render(request, 'app/doctor_notif_page.html',context)

