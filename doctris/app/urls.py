from django.urls import path

from .all_views import core, admin, doctor, patient, landing

app_name = 'app'

urlpatterns = [

    
    #basic routes
    path('', core.index, name='index'),
    path('landing/', core.landing, name='landing'),
    path('signup/', landing.signup, name='signup'),
    path('login/', core.login_user, name='login'),
    path('logout/', core.logout_user, name='logout'),
    #core handler routes
    path('appointments/delete/<str:pk>', core.appointments_delete, name='appointmentdelete'),
    path('notification/toggle/<str:pk>', core.notification_toggle_seen, name='notiftoggle'),
    path('notification/delete/<str:pk>', core.notification_delete, name='notifdelete'),
    path('reminder/disable/', core.disable_reminder, name='disablereminder'),
    
    #admin home route
    path('admin/<str:tab>', admin.admin, name='admin'),
    #admin doctor routes
    path('admin/add/doctor', admin.admin_doc_form_add, name='adminadddoc'),
    path('admin/edit/doctor/<str:un>', admin.admin_doc_form_edit, name='admineditdoc'),
    path('admin/delete/doctor/<str:username>', admin.admin_doc_delete, name='admindeletedoc'),
    #admin parient routes
    path('admin/add/patient', admin.admin_pat_form_add, name='adminaddpat'),
    path('admin/edit/patient/<str:un>', admin.admin_pat_form_edit, name='admineditpat'),
    path('admin/delete/patient/<str:username>', admin.admin_pat_delete, name='admindeletepat'),
    #admin review appointments

    
    #doctor profile route
    path('doctor/', doctor.doctor, name='doctor'),
    #doctor appointment routes
    path('doctor/appointments', doctor.doctor_appointments_view, name='doctorappointments'),
    path('doctor/appointments/reminder', doctor.doctor_appointments_view_reminder, name='doctorappointmentsreminder'),
    path('doctor/notifications', doctor.doctor_notifications_view, name='doctornotif'),
    path('doctor/appointment/<str:pk>', doctor.doctor_appointment_edit, name='doctorappointmentsedit'),
    #doctor info route
    path('doctor/editinfo', doctor.doctor_edit_info, name='doctoreditinfo'),
    path('doctor/editcred', doctor.doctor_edit_cred, name='doctoreditcred'),
    #doctor actions route
    path('doctor/action/spec/<str:pk>', doctor.doctor_spec_relation, name='doctoractionspec'),
    path('doctor/action/aff/<str:pk>', doctor.doctor_aff_relation, name='doctoractionaff'),
    path('doctor/action/avail/<str:pk>', doctor.doctor_avail_relation, name='doctoractionavail'),
    path('doctor/delete/<str:rel_name>/<str:pk>', doctor.doctor_delete_relation, name='doctordeleterelation'),
    
    
    #patient profile route
    path('patient/', patient.patient, name='patient'),
    #patient home route
    path('patient/home', patient.patient_home, name='patienthome'),
    #patient notification route
    path('patient/notifications', patient.patient_notifications_view, name='patientnotif'),
    #patient info route
    path('patient/editinfo', patient.patient_edit_info, name='patienteditinfo'),
    path('patient/editcred', patient.patient_edit_cred, name='patienteditcred'),
    #patient  appointments route
    path('patient/appointments', patient.patient_appointments_view, name='patientappointments'),
    path('patient/appointment/<str:uname>/<str:pk>', patient.patient_doctor_appointment, name='patientdocappoint'),
    path('patient/appointments/reminder', patient.patient_appointments_view_reminder, name='patientappointmentsreminder'),
    path('patient/doctor/<str:uname>', patient.patient_doctor_view, name='patientdocview'),
    
    
]