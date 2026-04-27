from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SeekerProfile, RecruiterProfile


class SeekerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile = forms.CharField(max_length=15)
    skills = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                            help_text="Enter skills separated by commas")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            SeekerProfile.objects.create(
                user=user,
                mobile=self.cleaned_data['mobile'],
                skills=self.cleaned_data['skills']
            )
        return user


class RecruiterRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=200)
    mobile = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            RecruiterProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                mobile=self.cleaned_data['mobile']
            )
        return user


class SeekerProfileForm(forms.ModelForm):
    class Meta:
        model = SeekerProfile
        fields = ['mobile', 'skills', 'resume', 'experience_years', 
                  'education', 'location', 'bio']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'mobile', 'company_website', 
                  'company_description', 'location']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }
