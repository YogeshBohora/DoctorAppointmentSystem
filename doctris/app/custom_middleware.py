from django.shortcuts import redirect
from .util import get_auth_group_name
from app.models import Appointment, Appointment_Status
from django.shortcuts import get_object_or_404
from .models import Reminder
from datetime import date
from app.models import Doctor, Patient, Doctor_Specialty, Hospital_Affiliation, Doctor_Avaliability, Doctor_Unavaliable_Date, Appointment, Appointment_Status, Reminder
class CheckUser(object):

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        url_name = request.resolver_match.url_name
        doctor_urls = ['doctor','doctorappointments','doctorappointmentsedit','doctoreditinfo','doctoreditcred','doctoractionspec','doctoractionaff','doctoractionavail','doctordeleterelation']
        patient_urls = ['patient','patienthome','patienteditinfo','patienteditcred','patientappointments','patientdocappoint','patientdocview']
        free_urls = [ 'index', 'login', 'logout', 'signup' ]

        # for redirrecting to login page if not logged in (except for guard free routes)
        if not url_name in free_urls:
            if not request.user.is_authenticated:
                return redirect('app:login')

        #if logged in user teies to goto index, 
        # redirrect them to corresponding dashboard page
        if url_name in ['index']:
            if get_auth_group_name(request) == 'administrator':
                print("admin->doctor page")
                return redirect('app:admin', tab="doctor")
            elif get_auth_group_name(request) == 'doctor':
                today = date.today()
                try:
                    reminder = Reminder.objects.get(username=request.user, date=today)
                    if reminder.restricted:
                        #redirrect to reminders page if restricted
                        return redirect('app:doctorappointments')
                    else:
                        #redirrect to appointments page if not restricted
                        return redirect('app:doctorappointmentsreminder')
                except:
                    new_reminder = Reminder(username=request.user, restricted=False, date=today)
                    new_reminder.save()
                    print("make new reminder")
                    return redirect('app:doctorappointmentsreminder')
                return redirect('app:doctorappointments')
            elif get_auth_group_name(request) == 'patient':
                today = date.today()
                try:
                    reminder = Reminder.objects.get(username=request.user, date=today)
                    if reminder.restricted:
                        #redirrect to reminders page if restricted
                        return redirect('app:patientappointments')
                    else:
                        #redirrect to appointments page if not restricted
                        return redirect('app:patientappointmentsreminder')
                except:
                    new_reminder = Reminder(username=request.user, restricted=False, date=today)
                    new_reminder.save()
                    return redirect('app:patientappointmentsreminder')
                return redirect('app:patienthome')
            else:
                pass
        #if an admin tries to delete an appointment, 
        # redirrect them to admin page
        if url_name in ['appointmentdelete']:
            if get_auth_group_name(request) == 'administrator':
                appoint = get_object_or_404(Appointment, pk=view_kwargs['pk'])
                canceled = Appointment_Status.objects.get(status="CANCELED")
                if(appoint.status != canceled):
                    return redirect('app:admin', tab='adminreviewappoint')
        #if user other than doctor tries top goto any of doctor urls, 
        # redirrect to the users home page  
        # for eg: if a patient tries to goto doctors/appointments, redirrect to patient/home
        if url_name in doctor_urls:
            if get_auth_group_name(request) == 'administrator':
                return redirect('app:admin', tab='doctor')
            elif get_auth_group_name(request) == 'patient':
                return redirect('app:patienthome')

        #if user other than patient tries top goto any of patient urls, 
        #redirrect to the users home page  
        # for eg: if a patient tries to goto doctors/appointments, redirrect to patient/home
        if url_name in patient_urls:
            if get_auth_group_name(request) == 'administrator':
                return redirect('app:admin', tab='doctor')
            elif get_auth_group_name(request) == 'doctor':
                return redirect('app:doctorappointments')
        
        
    def process_template_response(self,request,response):

        url_name = request.resolver_match.url_name
        
        # after successful login, redirrect the user to corresponding home page 
        if url_name in ['login']:
            if get_auth_group_name(request) == 'administrator':
                return redirect('app:admin' )
            elif get_auth_group_name(request) == 'patient':
                return redirect('app:patienthome')
            elif get_auth_group_name(request) == 'doctor':
                return redirect('app:doctor')
                
        # after successful appointment delete, redirrect to the users appointment page 
        if url_name in ['appointmentdelete']:
            if get_auth_group_name(request) == 'doctor':
                return redirect('app:doctorappointments')
            if get_auth_group_name(request) == 'patient':
                return redirect('app:patientappointments')
            if get_auth_group_name(request) == 'administrator':
                return redirect('app:admin', tab='adminreviewappoint')
        
        # after successful toggle of notification, redirrect to the users notification page 
        if url_name in ['notiftoggle']:
            if get_auth_group_name(request) == 'doctor':
                return redirect('app:doctornotif')
            if get_auth_group_name(request) == 'patient':
                return redirect('app:patientnotif')
            return redirect('app:index')