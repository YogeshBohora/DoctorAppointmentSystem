from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from ..util import get_auth_group_name
from ..models import Doctor, Patient, Appointment, Appointment_Status
from ..forms import UserForm

def admin(request, tab='doctor'):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:patienthome')
    else:
        if tab == 'patient':
            patients = Patient.objects.all()
            return render(request, 'app/admin_patient_tab.html',{"needs_login":needs_login, "patients":patients})
        elif tab == 'adminreviewappoint':
            canceled = Appointment_Status.objects.get(status="CANCELED")
            appointments = Appointment.objects.filter(status=canceled)
            print(appointments)
            return render(request, 'app/admin_review_appointments_tab.html',{"needs_login":needs_login, "review_appointments":appointments})
        else:
            doctors = Doctor.objects.all()
            return render(request, 'app/admin_doc_tab.html',{"needs_login":needs_login, "doctors":doctors})

def admin_doc_form_add(request):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        if request.method == 'POST':
            userForm = UserForm(request.POST or None)
            if userForm.is_valid():
                print("valid user")
                user = userForm.save(commit=False)
                password = userForm.cleaned_data['password']
                user.set_password(password)
                print(user.username, user.password)
                
                new_doctor = Doctor(username=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], phone=request.POST['phone'], admin_note=request.POST['admin_note'])
                print(new_doctor.username, new_doctor.full_name, new_doctor.email, new_doctor.phone, new_doctor.admin_note)
                doctorGroup = Group.objects.get(name='doctor')
                user.save()
                user.groups.set([doctorGroup])
                new_doctor.save()
                return render(request, 'app/admin_doc_form.html',{"needs_login":needs_login, "success": True})

            else:
                return render(request, 'app/admin_doc_form.html',{"needs_login":needs_login, "user_invalid":True})

        return render(request, 'app/admin_doc_form.html',{"needs_login":needs_login})


def admin_pat_form_add(request):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        if request.method == 'POST':
            userForm = UserForm(request.POST or None)
            if userForm.is_valid():
                user = userForm.save(commit=False)
                password = userForm.cleaned_data['password']
                user.set_password(password)
                
                new_patient = Patient(username=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], phone=request.POST['phone'], admin_note=request.POST['admin_note'])
                patientGroup = Group.objects.get(name='patient')
                user.save()
                user.groups.set([patientGroup])
                new_patient.save()
                return render(request, 'app/admin_pat_form.html',{"needs_login":needs_login, "success": True})

            else:
                return render(request, 'app/admin_pat_form.html',{"needs_login":needs_login, "user_invalid":True})

        return render(request, 'app/admin_pat_form.html',{"needs_login":needs_login})


def admin_doc_form_edit(request, un):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        doctor = get_object_or_404(Doctor, username=un)
        if request.method == "POST":
            user = User.objects.get(username=un)
            user.username = request.POST['username']
            doctor.first_name = request.POST['first_name']
            doctor.last_name = request.POST['last_name']
            doctor.email = request.POST['email']
            doctor.phone = request.POST['phone']
            doctor.admin_note = request.POST['admin_note']
            doctor.updated_on = timezone.now()
            user.save()
            doctor.username = user
            doctor.save()
            return render(request, 'app/admin_doc_form.html',{"needs_login":needs_login, "obj":doctor, "as_edit":True, "success":True})
        
        return render(request, 'app/admin_doc_form.html',{"needs_login":needs_login, "obj":doctor, "as_edit":True})

def admin_pat_form_edit(request, un):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        patient = get_object_or_404(Patient, username=un)
        if request.method == "POST":
            user = User.objects.get(username=un)
            user.username = request.POST['username']
            patient.first_name = request.POST['first_name']
            patient.last_name = request.POST['last_name']
            patient.email = request.POST['email']
            patient.phone = request.POST['phone']
            patient.admin_note = request.POST['admin_note']
            patient.updated_on = timezone.now()
            user.save()
            patient.username = user
            patient.save()
            return render(request, 'app/admin_pat_form.html',{"needs_login":needs_login, "obj":patient, "as_edit":True, "success":True})
        
        return render(request, 'app/admin_pat_form.html',{"needs_login":needs_login, "obj":patient, "as_edit":True})

def admin_doc_delete(request, username):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        user = User.objects.get(username=username)
        user.delete()
        return redirect('app:admin', tab="doctor")


def admin_pat_delete(request, username):
    needs_login = not request.user.is_authenticated
    if needs_login:
        return redirect('app:login')
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:index')
    else:
        user = User.objects.get(username=username)
        user.delete()
        return redirect('app:admin', tab="patient")