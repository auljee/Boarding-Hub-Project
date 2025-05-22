from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import HouseOwnerRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import HouseOwner, Room, Tenant
from .forms import RoomForm
from django.shortcuts import get_object_or_404
from .forms import TenantRegistrationForm
from .forms import TenantEditForm
from .models import Tenant, Payment
from .forms import PaymentForm
from datetime import datetime
from django.contrib import messages
from django.db.models import Prefetch
from .forms import HouseOwnerProfileForm
from .forms import TenantImageForm



def home(request):
    return render(request, 'core/home.html')

def owner_register(request):
    if request.method == 'POST':
        form = HouseOwnerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = HouseOwnerRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def owner_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # or change to your desired landing page
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def dashboard(request):
    owner_profile = get_object_or_404(HouseOwner, user=request.user)

    # Fetch rooms and tenants (without filtering on non-existent fields)
    rooms = Room.objects.filter(owner=owner_profile).prefetch_related(
        Prefetch('tenant_set')
    )

    return render(request, 'core/dashboard.html', {
        'owner': owner_profile,
        'rooms': rooms 
    })

@login_required
def add_room(request):
    owner_profile = get_object_or_404(HouseOwner, user=request.user)
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = owner_profile
            room.save()
            return redirect('dashboard')
    else:
        form = RoomForm()
    
    return render(request, 'core/add_room.html', {'form': form})

def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, owner=request.user.houseowner)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/edit_room.html', {'form': form})

def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, owner=request.user.houseowner)
    if request.method == 'POST':
        room.delete()
        return redirect('dashboard')
    return render(request, 'core/delete_room.html', {'room': room})

@login_required
def tenant_register(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()  # Don't pass user here anymore
            return redirect('dashboard')
    else:
        form = TenantRegistrationForm(user=request.user)

    return render(request, 'core/tenant_register.html', {'form': form})


@login_required
def add_tenant(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST, user=request.user)  # 👈 Pass user here
        if form.is_valid():
            form.save(user=request.user)  # 👈 Pass user again when saving
            return redirect('dashboard')
    else:
        form = TenantRegistrationForm(user=request.user)  # 👈 Also pass here
    return render(request, 'core/add_tenant.html', {'form': form})



def tenant_detail(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    return render(request, 'core/tenant_detail.html', {'tenant': tenant})

def tenant_edit(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = TenantEditForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            return redirect('tenant_detail', tenant_id=tenant.id)
    else:
        form = TenantEditForm(instance=tenant)
    return render(request, 'core/tenant_edit.html', {'form': form})

@login_required
def delete_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        tenant.delete()
        messages.success(request, "Tenant deleted successfully.")
        return redirect('dashboard')  # Change this to your actual dashboard URL name

    return render(request, 'core/tenant_delete.html', {'tenant': tenant})


def add_payment(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.tenant = tenant
            payment.save()
            return redirect('tenant_detail', tenant_id=tenant.id)
    else:
        form = PaymentForm(initial={'tenant': tenant})

    return render(request, 'core/add_payment.html', {
        'form': form,
        'tenant': tenant
    })
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from .models import Tenant

def tenant_pdf_view(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    payments = tenant.payments.all().order_by('-date_paid')  # use correct related_name and field
    owner = tenant.room.owner

    template_path = 'core/tenant_pdf.html'  # this should be your PDF template
    context = {
        'tenant': tenant,
        'payments': payments,
        'current_year': datetime.now().year,
        'owner': owner,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_history_{tenant.full_name}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

def payment_history(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    payments = tenant.payments.all().order_by('-date_paid')
    
    # For calendar: we just need paid dates and status
    calendar_data = [
        {
            "title": f"Paid: {payment.amount}",
            "start": payment.date_paid.strftime("%Y-%m-%d"),
            "color": "#4CAF50" if payment.status == "paid" else "#f44336"
        }
        for payment in payments
    ]

    return render(request, 'core/payment_history.html', {
        'tenant': tenant,
        'payments': payments,
        'calendar_data': calendar_data
    })

# views.py




@login_required
def edit_tenant_image(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = TenantImageForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            form.save()
            return redirect('tenant_detail', tenant_id=tenant.id)
    else:
        form = TenantImageForm(instance=tenant)
    return render(request, 'core/edit_tenant_image.html', {'form': form, 'tenant': tenant})


@login_required
def edit_profile(request):
    owner = get_object_or_404(HouseOwner, user=request.user)
    if request.method == 'POST':
        form = HouseOwnerProfileForm(request.POST, request.FILES, instance=owner)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = HouseOwnerProfileForm(instance=owner)
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def room_list(request):
    owner = get_object_or_404(HouseOwner, user=request.user)
    rooms = Room.objects.filter(owner=owner)
    return render(request, 'core/rooms.html', {'rooms': rooms})


@login_required
def tenant_list(request):
    owner = get_object_or_404(HouseOwner, user=request.user)
    tenants = Tenant.objects.filter(room__owner=owner)
    return render(request, 'core/tenants.html', {'tenants': tenants})

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'core/change_password.html'  # update path here
    success_url = reverse_lazy('password_change_done')  # or another URL

from rest_framework import viewsets
from .models import Room, Tenant, Payment
from api.serializers import RoomSerializer, TenantSerializer, PaymentSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer