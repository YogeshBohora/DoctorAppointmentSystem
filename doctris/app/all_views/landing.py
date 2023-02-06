from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from ..util import get_auth_group_name
from ..models import Doctor, Patient, Appointment, Appointment_Status
from ..forms import UserForm

def signup(request):
    needs_login = not request.user.is_authenticated
    if needs_login:
        if request.method == 'POST':
            userForm = UserForm(request.POST or None)
            if userForm.is_valid():
                user = userForm.save(commit=False)
                password = userForm.cleaned_data['password']
                user.set_password(password)
                new_patient = Patient(username=user, first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], phone=request.POST['phone'], admin_note="-")
                patientGroup = Group.objects.get(name='patient')
                user.save()
                user.groups.set([patientGroup])
                new_patient.save()
                return render(request, 'app/pat_form.html',{"needs_login":needs_login, "success": True})
            else:
                return render(request, 'app/pat_form.html',{"needs_login":needs_login, "user_invalid":True})
        return render(request, 'app/pat_form.html',{"needs_login":needs_login})
    elif get_auth_group_name(request) == 'doctor':
        return redirect('app:doctor')
    elif get_auth_group_name(request) == 'patient':
        return redirect('app:patienthome')
    else:
        return redirect('app:admin', 'doctor')