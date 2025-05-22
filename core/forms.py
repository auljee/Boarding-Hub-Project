from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HouseOwner
from .models import Room
from .models import Tenant
from .models import HouseOwner 
from .models import Payment

class HouseOwnerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    boarding_house_name = forms.CharField(label="Name of your Boarding House")
    profile_image = forms.ImageField(required=False)  # optional field for the profile image

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            house_name = self.cleaned_data['boarding_house_name']
            profile_image = self.cleaned_data.get('profile_image')
            house_owner = HouseOwner.objects.create(user=user, boarding_house_name=house_name)
            if profile_image:
                house_owner.profile_image = profile_image
                house_owner.save()
        return user

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'capacity']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class TenantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['full_name', 'contact_number', 'email', 'room']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Store user
        super().__init__(*args, **kwargs)
        if self.user:
            try:
                house_owner = HouseOwner.objects.get(user=self.user)
                self.fields['room'].queryset = Room.objects.filter(owner=house_owner)
            except HouseOwner.DoesNotExist:
                self.fields['room'].queryset = Room.objects.none()
        else:
            self.fields['room'].queryset = Room.objects.none()

    def save(self, commit=True):
        tenant = super().save(commit=False)
        # You can now use self.user if needed
        if commit:
            tenant.save()
        return tenant


class TenantEditForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            'full_name', 'contact_number', 'email', 'address',
            'guardian_name', 'guardian_contact', 'guardian_address',
            'due_date', 'payment_status', 'room', 'rent_fee',
            'advance_payment', 'deposit', 'status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_address': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'rent_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'advance_payment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select status-select'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['tenant','month', 'amount','status', 'notes']  # Use the correct model fields
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.TextInput(attrs={'class': 'form-control'}), 
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),  # 'amount' instead of 'amount_paid'
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),  # Optional notes
        }

class HouseOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = HouseOwner
        fields = ['boarding_house_name', 'profile_image']
        widgets = {
            'boarding_house_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TenantImageForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['tenant_image']
