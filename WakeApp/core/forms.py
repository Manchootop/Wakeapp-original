from django import forms
from django.forms import ModelForm

from WakeApp.core.models import Event


# class BootstrapFormMixin:
#     fields = {}
#
#     def _init_bootstrap_form_controls(self):
#         for _, field in self.fields.items():
#             if not hasattr(field.widget, 'attrs'):
#                 setattr(field.widget, 'attrs', {})
#             if 'class' not in field.widget.attrs:
#                 field.widget.attrs['class'] = ''
#             field.widget.attrs['class'] += ' form-control'


class CreateEventForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


    def save(self, commit=True):
        # commit false does not persist to database
        # just returns the object to be created
        event = super().save(commit=False)

        event.user = self.user
        if commit:
            event.save()

        return event

    class Meta:
        model = Event
        fields = ('type', 'title', 'description', 'location', 'recommendations',)
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Заглавие',
                }
            ),
            'type': forms.ChoiceField(
                attrs={
                    'class': 'form-control',
                    'help_text': 'Изберете вид на събитието',
                }
            ),
            'description': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Описание',
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Местоположение',
                }
            ),
            'recommendations': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Препоръки',
                }
            ),
        }