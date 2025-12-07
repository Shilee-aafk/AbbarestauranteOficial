from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django import forms
from .models import PinRegistro

class CustomUserCreationForm(UserCreationForm):
    pin = forms.CharField(
        max_length=10, 
        help_text="Ingresa el PIN de registro proporcionado por el administrador."
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
            'placeholder': 'Nombre de usuario'
        })
        self.fields['pin'].widget.attrs.update({
            'class': f'{common_classes} rounded-none',
            'placeholder': 'PIN de Registro'
        })
        self.fields['password1'].widget.attrs.update({
            'class': f'{common_classes} rounded-none',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': f'{common_classes} rounded-b-md',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_pin(self):
        pin_value = self.cleaned_data.get("pin")
        try:
            pin_obj = PinRegistro.objects.get(pin=pin_value, used_by__isnull=True)
            # Guardamos el objeto pin para usarlo en el método save()
            self.pin_obj = pin_obj
        except PinRegistro.DoesNotExist:
            raise forms.ValidationError("Este PIN no es válido o ya ha sido utilizado.")
        return pin_value

    def save(self, commit=True):
        # Guardar el usuario
        user = super().save(commit=False)
        if commit:
            user.save()
            # Asignar el grupo y marcar el PIN como usado
            if hasattr(self, 'pin_obj'):
                user.groups.add(self.pin_obj.group)
                self.pin_obj.used_by = user
                self.pin_obj.save()
        return user