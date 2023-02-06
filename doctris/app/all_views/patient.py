from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from ..util import get_auth_group_name, compare_weekday, Database_Accessor as DA, NotificationManager as NM, STATUS
from ..models import Doctor, Patient, Doctor_Specialty, Hospital_Affiliation, Doctor_Avaliability, Doctor_Unavaliable_Date, Appointment, Appointment_Status, Payment, Notification, Reminder
from ..forms import DoctorForm, UserForm
from datetime import datetime
import datetime as dt
import requests, json

def patient(request):
    needs_login = not request.user.is_authenticated

    patient = get_object_or_404(Patient, username=request.user)
    return render(request, 'app/patient_profile_page.html',{"needs_login":needs_login, "patient":patient})

def patient_edit_info(request):
    needs_login = not request.user.is_authenticated

    patient = get_object_or_404(Patient, username=request.user)
    if request.method == "POST":
        password = request.POST['password']
        patuser = get_object_or_404(User, username=request.user)
        patient.first_name = request.POST['first_name']
        patient.last_name = request.POST['last_name']
        patient.email = request.POST['email']
        patient.phone = request.POST['phone']
        if patuser.check_password(password):
            patient.save()
            return render(request, 'app/patient_profile_edit.html',{"needs_login":needs_login, "obj":patient, "success":True})
        return render(request, 'app/patient_profile_edit.html',{"needs_login":needs_login, "password_invalid":True, "obj":patient})
    return render(request, 'app/patient_profile_edit.html',{"needs_login":needs_login, "obj":patient})

def patient_edit_cred(request):
    needs_login = not request.user.is_authenticated

    patient = get_object_or_404(Patient, username=request.user)
    if request.method == "POST":
        old_password = request.POST['old_password']
        patuser = get_object_or_404(User, username=request.user)
        if patuser.check_password(old_password):
            if request.POST['new_password'] == request.POST['confirm_password']:
                patuser.username = request.POST['username']
                patient.username = patuser
                patuser.set_password(request.POST['new_password'])
                try:
                    patuser.save()
                    patient.save()
                    return redirect('app:login')
                except IntegrityError:
                    return render(request, 'app/patient_profile_edit_cred.html',{"needs_login":needs_login, "obj":patient, "user_error":True })
            return render(request, 'app/patient_profile_edit_cred.html',{"needs_login":needs_login, "obj":patient, "confirm_invalid":True })
        return render(request, 'app/patient_profile_edit_cred.html',{"needs_login":needs_login, "password_invalid":True, "obj":patient})
    return render(request, 'app/patient_profile_edit_cred.html',{"needs_login":needs_login, "obj":patient})

def patient_home(request):
    needs_login = not request.user.is_authenticated

    patient = get_object_or_404(Patient, username=request.user)
    doctors = Doctor.objects.prefetch_related('specialty','affiliation','avaliability')
    metadata = {'avails':[], 'specialty':[]}
    for doc in doctors:
        metadata['avails'].append({ 'data': doc.avaliability.values_list('day_in_week','starting_time', 'ending_time'), 'username':doc.username })
    for doc in doctors:
        metadata['specialty'].append({ 'data': doc.specialty.values_list('specialization_in','description'), 'username':doc.username })
    return render(request, 'app/patient_home_page.html',{"needs_login":needs_login, "obj":patient,"doctors":doctors, "metadata":metadata})

def patient_doctor_view(request, uname ):
    needs_login = not request.user.is_authenticated

    doctor = get_object_or_404(Doctor, username=uname)
    specializations = Doctor_Specialty.objects.filter(doctor=doctor)
    hospitals = Hospital_Affiliation.objects.filter(doctor=doctor)
    avaliability = Doctor_Avaliability.objects.filter(doctor=doctor)
    return render(request, 'app/patient_doctor_view.html',{"needs_login":needs_login, "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability})

def patient_doctor_appointment(request, uname, pk ):
    needs_login = not request.user.is_authenticated
    
    today = dt.date.today().strftime("%Y-%m-%d")
    patient = get_object_or_404(Patient, username=request.user)
    doctor = get_object_or_404(Doctor, username=uname)
    specializations = Doctor_Specialty.objects.filter(doctor=doctor)
    hospitals = Hospital_Affiliation.objects.filter(doctor=doctor)
    avaliability = Doctor_Avaliability.objects.filter(doctor=doctor)
    appointments = Appointment.objects.filter(doctor=doctor)
    appointment_to_edit = None
    as_edit = False
    if not pk == '-1':
        appointment_to_edit =  get_object_or_404(Appointment, pk=pk)
        appointment_to_edit.visit_date = appointment_to_edit.visit_date.strftime("%Y-%m-%d")
        appointment_to_edit.start_time = appointment_to_edit.start_time.strftime("%H:%M")
        appointment_to_edit.end_time = appointment_to_edit.end_time.strftime("%H:%M")
        as_edit = True
    
    if request.method == "POST":
        visit_date = request.POST['visit_date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        invite_reason = request.POST['invite_reason']
        visit_date_object = datetime.strptime(visit_date, "%Y-%m-%d")
        starttime_object = datetime.strptime(start_time, "%H:%M")
        endtime_object = datetime.strptime(end_time, "%H:%M")
        if starttime_object >= endtime_object:
            return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability, "appointments":appointments, "today_date":today, "invalid_time": True, "as_edit":as_edit, "obj":appointment_to_edit})

        # check if start time and end time  is avaliable for doctor
        
        # check if the visit date is in avaliableweekday
        is_weekday_avail = False
        doc_avail_weekday = []
        for avail in avaliability:
            if compare_weekday( visit_date_object.weekday(),  avail.day_in_week):
                is_weekday_avail = True
                doc_avail_weekday.append(avail)
        if not is_weekday_avail:
            return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "invalid_weekday": True, "as_edit":as_edit, "obj":appointment_to_edit})

        if is_weekday_avail:
            is_time_avaliable = False
            doc_avail_weekday_time = []
            # check if the appointment time falls in general avaliable time for the day
            for avail in doc_avail_weekday:
                if avail.starting_time <= starttime_object.time() and avail.ending_time >= endtime_object.time() :
                    is_time_avaliable = True
                    doc_avail_weekday_time.append(avail)
            
            if not is_time_avaliable:
                return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability, "appointments":appointments, "today_date":today, "invalid_appointment_time": True, "as_edit":as_edit, "obj":appointment_to_edit})
            
            #now checking if the starttime and end time of new appointment conflicts with any other appointment the doctor has that day  
            all_appointments_for_doc = Appointment.objects.filter(doctor=doctor, visit_date=visit_date_object.date())
            has_appointment_collision = False
            for appoint in all_appointments_for_doc:
                if(appoint.start_time < starttime_object.time() and appoint.end_time > starttime_object.time()) or (appoint.start_time < endtime_object.time() and appoint.end_time > endtime_object.time()):
                    has_appointment_collision = True

            if has_appointment_collision:
                return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability, "appointments":appointments,"today_date":today, "has_appointment_collision": True, "as_edit":as_edit, "obj":appointment_to_edit})
            
            #the new appointment is okay. Make a new Appointment and send success message.
            # latter, we will hook it to khalti api anmd provide a callback here 
            incomplete_status = Appointment_Status.objects.get(status="INCOMPLETE")
            if pk == '-1':
                # server side verification here
                if 'config' in request.POST:
                    print('making new Appointment')
                    config = json.loads(request.POST['config'])
                    payload = {
                    "token":  config["token"],
                    "amount": 1000
                    }
                    headers = {
                    "Authorization": "Key test_secret_key_ff73da8104984199aa10c2c3ea180c70"
                    }
                    response = requests.post("https://khalti.com/api/v2/payment/verify/", payload, headers = headers)
                    if response.status_code == 200 :
                        print('transaction was successful')
                        if config["amount"] == 1000:
                            payment_info =  response.json()
                            print(payment_info)
                            print(payment_info["idx"])
                            payment = Payment(idx=payment_info["idx"], type_idx=payment_info["type"]["idx"], type_name=payment_info["type"]["name"], state_idx=payment_info["state"]["idx"], state_name=payment_info['state']['name'], amount=payment_info['amount'],created_on=payment_info['created_on'] )
                            payment.save()
                            
                            new_appoint = Appointment(doctor=doctor, patient=patient, status=incomplete_status, visit_date=visit_date_object.date(), start_time=start_time, end_time=end_time, invite_reason=invite_reason, payment=payment )
                            
                            new_appoint.save()

                            #make a mew notification object
                            doctor_notification_config = {
                                "user":new_appoint.doctor,
                                "title":"You have new appointment with {pat_full_name} on {visit_date}".format(visit_date=visit_date,pat_full_name=new_appoint.patient.full_name),
                                "description":"{pat_full_name} booked a new appointment on {visit_date} from {start_time} to {end_time}".format(visit_date=visit_date,pat_full_name=new_appoint.patient.full_name, start_time=start_time, end_time=end_time)
                            }
                            patient_notification_config = {
                                "user":new_appoint.patient,
                                "title":"Successfully booked New Appointment with {doc_full_name} on {visit_date}".format(visit_date=visit_date,doc_full_name=new_appoint.doctor.full_name),
                                "description":"New appointment booked with {doc_full_name} on {visit_date} from {start_time} to {end_time}".format(visit_date=visit_date,doc_full_name=new_appoint.doctor.full_name, start_time=start_time, end_time=end_time)
                            }
                            NM.create_noticication(doctor_notification_config)
                            NM.create_noticication(patient_notification_config)
                            try:
                                today = dt.date.today()
                                reminder = Reminder.objects.get(username=new_appoint.doctor.username, date=today)
                                reminder.restricted=False
                                reminder.save()
                            except:
                                new_reminder = Reminder(username=new_appoint.doctor.username, restricted=False, date=today)
                                new_reminder.save()
                            print("saved new appointment")
                    return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "success":True, "as_edit":as_edit, "obj":appointment_to_edit})
                else:
                    print('asking for verification')
                    new_appoint = Appointment(doctor=doctor, patient=patient, status=incomplete_status, visit_date=visit_date_object.date(), start_time=start_time, end_time=end_time, invite_reason=invite_reason )
                    new_appoint.visit_date = new_appoint.visit_date.strftime("%Y-%m-%d")
                    
                    appointment_POST_data = {}
                    for key,val in request.POST.items():
                        appointment_POST_data.update({ key : val})
                    return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "success":False, "as_edit":True, "obj":new_appoint, "show_payment":True, "appointment_POST_data":appointment_POST_data})
                
                return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "success":True, "as_edit":as_edit, "obj":appointment_to_edit})

            else:
                doctor_notification_config = {
                    "user":appointment_to_edit.doctor,
                    "title":"{pat_name} Updated appointment of {prev_visit_date}".format(prev_visit_date=appointment_to_edit.visit_date, pat_name=appointment_to_edit.patient.full_name),
                    "description":"{pat_name} updated appointment of date {prev_visit_date} ( from {prev_start_time} - {prev_end_time} ) to date {visit_date} ( from {start_time} - {end_time} )".format(pat_name=appointment_to_edit.patient.full_name, prev_visit_date=appointment_to_edit.visit_date, prev_start_time=appointment_to_edit.start_time, prev_end_time=appointment_to_edit.end_time, visit_date=visit_date, start_time=start_time, end_time=end_time )
                }
                patient_notification_config = {
                    "user":appointment_to_edit.patient,
                    "title":"You have successfully updated appointment of {prev_visit_date} with {doc_name}".format(prev_visit_date=appointment_to_edit.visit_date, doc_name=appointment_to_edit.doctor.full_name),
                    "description":"Your appointment with {doc_name} of date {prev_visit_date} (from {prev_start_time} - {prev_end_time}) has been successfully updated to date {visit_date} (from {start_time} - {end_time})".format(doc_name=appointment_to_edit.doctor.full_name, prev_visit_date=appointment_to_edit.visit_date, prev_start_time=appointment_to_edit.start_time, prev_end_time=appointment_to_edit.end_time, visit_date=visit_date, start_time=start_time, end_time=end_time )
                }
                appointment_to_edit.visit_date=visit_date_object.date()
                appointment_to_edit.start_time=start_time
                appointment_to_edit.end_time=end_time
                appointment_to_edit.invite_reason=invite_reason
                appointment_to_edit.save()
                NM.create_noticication(doctor_notification_config)
                NM.create_noticication(patient_notification_config)
                try:
                    today = dt.date.today()
                    reminder = Reminder.objects.get(username=appointment_to_edit.doctor.username, date=today)
                    reminder.restricted=False
                    reminder.save()
                except:
                    new_reminder = Reminder(username=appointment_to_edit.doctor.username, restricted=False, date=today)
                    new_reminder.save()
                return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "success":True, "as_edit":as_edit, "obj":appointment_to_edit, "payment_done":True})
    # for get requests
    return render(request, 'app/patient_doctor_appointment.html',{"needs_login":needs_login, "patient": patient , "doctor":doctor, "specializations":specializations, "hospitals":hospitals, "avaliability":avaliability,"appointments":appointments, "today_date":today, "as_edit":as_edit, "obj":appointment_to_edit })

def patient_appointments_view(request):
    patient = get_object_or_404(Patient, username=request.user)
    appointments = DA.patient_appointments_record(patient)
    labeled_appointments = DA.label_appointments(appointments)
    context= {
        "needs_login":False,
        "upcomming_appointments": labeled_appointments["upcomming"],
        "past_appointments": labeled_appointments["past"],
        "todays_appointments": labeled_appointments["todays"],
    }
    return render(request, 'app/patient_appointments_view.html',context)


def patient_appointments_view_reminder(request):
    patient = get_object_or_404(Patient, username=request.user)
    appointments = DA.patient_appointments_record(patient)
    labeled_reminders = DA.label_reminders(appointments)
    notifications = Notification.objects.filter(username=request.user.username, status=STATUS["UNSEEN"])
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
    return render(request, 'app/patient_reminder_page.html',context)


def patient_notifications_view(request):
    patient = get_object_or_404(Patient, username=request.user)
    notifications = Notification.objects.filter(username=patient.username)
    seen = notifications.filter(status=STATUS["SEEN"])
    unseen = notifications.filter(status=STATUS["UNSEEN"])
    context={
        "needs_login":False,
        "seen":seen,
        "unseen":unseen,
    }
    return render(request, 'app/patient_notif_page.html',context)

