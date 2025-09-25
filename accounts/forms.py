from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('skills', 'location', 'projects')
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'projects': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    # 1. Add the new field for selecting user type
    user_type = forms.ChoiceField(
        choices= (('regular', 'Job Seeker'), ('recruiter', 'Recruiter')),
        widget=forms.RadioSelect, # Renders as radio buttons
        label="I am a:",
        required=True
    )

    # #Add an email field, which is not included by default
    # class Meta(UserCreationForm.Meta):
    #     fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']: #would add email here if we added it
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update( {'class': 'form-control'} )