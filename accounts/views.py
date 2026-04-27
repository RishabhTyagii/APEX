from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import (SeekerRegistrationForm, RecruiterRegistrationForm,
                   SeekerProfileForm, RecruiterProfileForm)
from .models import SeekerProfile, RecruiterProfile
from jobs.models import Job


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


def register_seeker(request):
    if request.method == 'POST':
        form = SeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('seeker_profile')
    else:
        form = SeekerRegistrationForm()
    return render(request, 'accounts/register_seeker.html', {'form': form})


def register_recruiter(request):
    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('recruiter_profile')
    else:
        form = RecruiterRegistrationForm()
    return render(request, 'accounts/register_recruiter.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    
    # Check user role
    if hasattr(user, 'seeker_profile'):
        profile = user.seeker_profile
        seeker_skills = profile.get_skills_list()
        
        # Get recommended jobs based on skills
        all_jobs = Job.objects.filter(is_active=True).order_by('-created_at')
        recommended_jobs = []
        
        for job in all_jobs:
            job_skills = job.get_skills_list()
            match_count = len(set(seeker_skills) & set(job_skills))
            if match_count > 0:
                job.match_score = match_count
                recommended_jobs.append(job)
        
        recommended_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        context = {
            'role': 'seeker',
            'profile': profile,
            'recommended_jobs': recommended_jobs[:10],
            'all_jobs': all_jobs[:20]
        }
        
    elif hasattr(user, 'recruiter_profile'):
        profile = user.recruiter_profile
        my_jobs = Job.objects.filter(recruiter=profile).order_by('-created_at')
        
        context = {
            'role': 'recruiter',
            'profile': profile,
            'my_jobs': my_jobs
        }
    else:
        return redirect('home')
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def seeker_profile(request):
    try:
        profile = request.user.seeker_profile
    except SeekerProfile.DoesNotExist:
        return redirect('register_seeker')
    
    if request.method == 'POST':
        form = SeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('seeker_profile')
    else:
        form = SeekerProfileForm(instance=profile)
    
    return render(request, 'accounts/seeker_profile.html', {
        'form': form,
        'profile': profile
    })


@login_required
def recruiter_profile(request):
    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return redirect('register_recruiter')
    
    if request.method == 'POST':
        form = RecruiterProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('recruiter_profile')
    else:
        form = RecruiterProfileForm(instance=profile)
    
    return render(request, 'accounts/recruiter_profile.html', {
        'form': form,
        'profile': profile
    })
