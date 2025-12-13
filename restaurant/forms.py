from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django import forms
from .models import RegistrationPin

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
        
        # Cambiar label de password2
        self.fields['password2'].label = 'Confirmar contraseña'

        # Personalizar mensajes de error a español
        self.error_messages = {
            'password_mismatch': 'Las contraseñas no coinciden.',
            'username_taken': 'Este nombre de usuario ya existe.',
        }
        
        self.fields['username'].error_messages = {
            'required': 'Este campo es requerido.',
            'unique': 'Este nombre de usuario ya existe.',
            'invalid': 'Ingresa un nombre de usuario válido.',
        }
        
        self.fields['password1'].error_messages = {
            'required': 'Este campo es requerido.',
        }
        
        self.fields['password2'].error_messages = {
            'required': 'Este campo es requerido.',
        }
        
        # Mensajes de validación de contraseña
        self.fields['password1'].help_text = (
            '<ul><li>Tu contraseña no puede ser demasiado similar a tu nombre de usuario.</li>'
            '<li>Tu contraseña debe contener al menos 8 caracteres.</li>'
            '<li>Tu contraseña no puede ser un número entero muy común.</li>'
            '<li>Tu contraseña no puede consistir únicamente en números.</li></ul>'
        )

    def clean_pin(self):
        pin_value = self.cleaned_data.get("pin")
        try:
            pin_obj = RegistrationPin.objects.get(pin=pin_value, used_by__isnull=True)
            # Save the pin object for use in the save() method
            self.pin_obj = pin_obj
        except RegistrationPin.DoesNotExist:
            raise forms.ValidationError("Este PIN no es válido o ya ha sido utilizado.")
        return pin_value

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return password2

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


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado con mensajes en español.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'invalid_login': 'Por favor, ingresa un nombre de usuario y contraseña correctos. Ten en cuenta que ambos campos pueden ser sensibles a mayúsculas y minúsculas.',
            'invalid_username': 'Este nombre de usuario no existe.',
            'inactive': 'Esta cuenta está inactiva.',
        }
