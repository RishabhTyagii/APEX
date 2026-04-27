from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from .ats import calculate_ats_score, rank_applications


def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Filter by job type
    job_type = request.GET.get('type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # If user is a seeker, calculate match scores
    if request.user.is_authenticated and hasattr(request.user, 'seeker_profile'):
        seeker_skills = set(request.user.seeker_profile.get_skills_list())
        for job in jobs:
            job_skills = set(job.get_skills_list())
            match_count = len(seeker_skills & job_skills)
            job.match_score = match_count
    
    context = {
        'jobs': jobs,
        'query': query,
        'job_type': job_type,
        'job_types': Job.JOB_TYPE_CHOICES,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    already_applied = False
    application = None
    
    if request.user.is_authenticated and hasattr(request.user, 'seeker_profile'):
        application = Application.objects.filter(
            job=job, 
            seeker=request.user.seeker_profile
        ).first()
        already_applied = application is not None
    
    context = {
        'job': job,
        'already_applied': already_applied,
        'application': application,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_job(request, pk):
    if not hasattr(request.user, 'seeker_profile'):
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('job_detail', pk=pk)
    
    job = get_object_or_404(Job, pk=pk)
    seeker = request.user.seeker_profile
    
    # Check if already applied
    if Application.objects.filter(job=job, seeker=seeker).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.seeker = seeker
            application.ats_score = calculate_ats_score(seeker, job)
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('my_applications')
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})


@login_required
def my_applications(request):
    if not hasattr(request.user, 'seeker_profile'):
        messages.error(request, 'Only job seekers can view applications.')
        return redirect('dashboard')
    
    applications = Application.objects.filter(
        seeker=request.user.seeker_profile
    ).select_related('job', 'job__recruiter')
    
    return render(request, 'jobs/my_applications.html', {'applications': applications})


@login_required
def post_job(request):
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user.recruiter_profile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('recruiter_jobs')
    else:
        form = JobForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job(request, pk):
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can edit jobs.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('recruiter_jobs')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


@login_required
def recruiter_jobs(request):
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can view this page.')
        return redirect('dashboard')
    
    jobs = Job.objects.filter(recruiter=request.user.recruiter_profile)
    
    return render(request, 'jobs/recruiter_jobs.html', {'jobs': jobs})


@login_required
def job_applications(request, pk):
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can view applications.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    applications = job.applications.all().select_related('seeker', 'seeker__user')
    
    # Sort by ATS score
    sort_by = request.GET.get('sort', 'ats')
    if sort_by == 'ats':
        applications = rank_applications(applications)
    elif sort_by == 'date':
        applications = applications.order_by('-applied_at')
    elif sort_by == 'status':
        applications = applications.order_by('status', '-ats_score')
    
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications,
        'sort_by': sort_by,
    })


@login_required
def update_application_status(request, pk):
    if request.method != 'POST':
        return redirect('dashboard')
    
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can update application status.')
        return redirect('dashboard')
    
    application = get_object_or_404(Application, pk=pk)
    
    # Verify the recruiter owns this job
    if application.job.recruiter != request.user.recruiter_profile:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('dashboard')
    
    new_status = request.POST.get('status')
    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()
        messages.success(request, f'Application status updated to {new_status}.')
    
    return redirect('job_applications', pk=application.job.pk)


@login_required
def view_applicant(request, pk):
    if not hasattr(request.user, 'recruiter_profile'):
        messages.error(request, 'Only recruiters can view applicant details.')
        return redirect('dashboard')
    
    application = get_object_or_404(Application, pk=pk)
    
    # Verify the recruiter owns this job
    if application.job.recruiter != request.user.recruiter_profile:
        messages.error(request, 'You do not have permission to view this applicant.')
        return redirect('dashboard')
    
    return render(request, 'jobs/view_applicant.html', {'application': application})
