from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django import forms
from .models import RegistrationPin

class CustomUserCreationForm(UserCreationForm):
    pin = forms.CharField(
        max_length=10, 
        help_text="Enter the registration PIN provided by the administrator."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common_classes = (
            "relative block w-full appearance-none border border-gray-300 px-3 py-3 "
            "text-gray-900 placeholder-gray-500 focus:z-10 focus:border-amber-500 "
            "focus:outline-none focus:ring-amber-500 sm:text-sm"
        )

        self.fields['username'].widget.attrs.update({
            'class': f'{common_classes} rounded-t-md',
            'placeholder': 'Username'
        })
        self.fields['pin'].widget.attrs.update({
            'class': f'{common_classes} rounded-none',
            'placeholder': 'Registration PIN'
        })
        self.fields['password1'].widget.attrs.update({
            'class': f'{common_classes} rounded-none',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': f'{common_classes} rounded-b-md',
            'placeholder': 'Confirm password'
        })

    def clean_pin(self):
        pin_value = self.cleaned_data.get("pin")
        try:
            pin_obj = RegistrationPin.objects.get(pin=pin_value, used_by__isnull=True)
            # Save the pin object for use in the save() method
            self.pin_obj = pin_obj
        except RegistrationPin.DoesNotExist:
            raise forms.ValidationError("This PIN is not valid or has already been used.")
        return pin_value

    def save(self, commit=True):
        # Save the user
        user = super().save(commit=False)
        if commit:
            user.save()
            # Asignar el grupo y marcar el PIN como usado
            if hasattr(self, 'pin_obj'):
                user.groups.add(self.pin_obj.group)
                self.pin_obj.used_by = user
                self.pin_obj.save()
        return user