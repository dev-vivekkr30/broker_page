from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from main.models import Broker, Colony
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import csv
import pandas as pd
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin:admin_dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('custom_admin:admin_dashboard')
        else:
            messages.error(request, 'Invalid email or password, or you do not have admin access.')
    # Clear all messages before rendering login
    from django.contrib import messages as django_messages
    list(django_messages.get_messages(request))
    return render(request, 'admin/login.html')

@login_required(login_url='/admin/login/')
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('custom_admin:admin_login')

@login_required(login_url='/admin/login/')
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    # Exclude admin/superadmin users
    brokers = Broker.objects.filter(is_staff=False, is_superuser=False).order_by('-id')
    total_users = brokers.count()
    verified_users = sum(1 for b in brokers if b.is_fully_verified)
    unverified_users = total_users - verified_users
    # Add pending_verifications count to each broker
    verification_fields = [
        'is_name_verified', 'is_photo_verified', 'is_company_verified',
        'is_age_verified', 'is_education_verified',
        'is_residence_colony_verified', 'is_office_address_verified'
    ]
    for broker in brokers:
        broker.pending_verifications = sum(1 for field in verification_fields if not getattr(broker, field))
    context = {
        'admin_user': request.user,
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'brokers': brokers,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required(login_url='/admin/login/')
def admin_users(request):
    return render(request, 'admin/users.html', {})

@login_required(login_url='/admin/login/')
def admin_view_details(request, broker_id):
    broker = Broker.objects.filter(id=broker_id).first()
    return render(request, 'admin/view_details.html', {'broker': broker})

@csrf_exempt
@require_POST
@login_required(login_url='/admin/login/')
def admin_toggle_verification(request, broker_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    broker = Broker.objects.filter(id=broker_id).first()
    field = request.POST.get('field')
    value = request.POST.get('value') == 'true'
    if field not in [
        'is_name_verified', 'is_photo_verified', 'is_company_verified',
        'is_age_verified', 'is_education_verified',
        'is_residence_colony_verified', 'is_office_address_verified'
    ]:
        return JsonResponse({'error': 'Invalid field'}, status=400)
    setattr(broker, field, value)
    broker.save()
    return JsonResponse({
        'success': True,
        'is_fully_verified': broker.is_fully_verified,
        'field': field,
        'value': value,
    })

@login_required(login_url='/admin/login/')
def admin_colonies(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    colonies = Colony.objects.all().order_by('name')
    context = {
        'admin_user': request.user,
        'colonies': colonies,
    }
    return render(request, 'admin/ColoniesArea.html', context)

@login_required(login_url='/admin/login/')
def admin_add_colony(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    if request.method == 'POST':
        colony_name = request.POST.get('colony_name', '').strip()
        if colony_name:
            # Check if colony already exists
            if Colony.objects.filter(name__iexact=colony_name).exists():
                messages.error(request, f'Colony "{colony_name}" already exists.')
            else:
                Colony.objects.create(name=colony_name)
                messages.success(request, f'Colony "{colony_name}" added successfully.')
        else:
            messages.error(request, 'Colony name is required.')
    
    return redirect('custom_admin:admin_colonies')

@login_required(login_url='/admin/login/')
def admin_edit_colony(request, colony_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    colony = get_object_or_404(Colony, id=colony_id)
    
    if request.method == 'POST':
        colony_name = request.POST.get('colony_name', '').strip()
        if colony_name:
            # Check if colony name already exists (excluding current colony)
            if Colony.objects.filter(name__iexact=colony_name).exclude(id=colony_id).exists():
                messages.error(request, f'Colony "{colony_name}" already exists.')
            else:
                colony.name = colony_name
                colony.save()
                messages.success(request, f'Colony updated successfully.')
        else:
            messages.error(request, 'Colony name is required.')
    
    return redirect('custom_admin:admin_colonies')

@login_required(login_url='/admin/login/')
def admin_delete_colony(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    if request.method == 'POST':
        colony_id = request.POST.get('colony_id')
        try:
            colony = Colony.objects.get(id=colony_id)
            colony_name = colony.name
            colony.delete()
            messages.success(request, f'Colony "{colony_name}" deleted successfully.')
        except Colony.DoesNotExist:
            messages.error(request, 'Colony not found.')
    
    return redirect('custom_admin:admin_colonies')

@login_required(login_url='/admin/login/')
def admin_export_colonies(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="colonies.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['S/N', 'Colony Name', 'Created Date'])
    
    colonies = Colony.objects.all().order_by('name')
    for index, colony in enumerate(colonies, 1):
        writer.writerow([index, colony.name, colony.created_at.strftime('%Y-%m-%d')])
    
    return response

@login_required(login_url='/admin/login/')
def admin_download_colonies_template(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="colonies_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Colony Name'])
    writer.writerow(['Example Colony 1'])
    writer.writerow(['Example Colony 2'])
    
    return response

@login_required(login_url='/admin/login/')
def admin_import_colonies(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin access.')
        return redirect('custom_admin:admin_login')
    
    if request.method == 'POST':
        uploaded_file = request.FILES.get('colonies_file')
        
        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('custom_admin:admin_colonies')
        
        try:
            # Read the file based on its extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Read CSV file
                df = pd.read_csv(uploaded_file)
            elif file_extension in ['xls', 'xlsx']:
                # Read Excel file
                df = pd.read_excel(uploaded_file)
            else:
                messages.error(request, 'Unsupported file format. Please upload CSV or Excel files.')
                return redirect('custom_admin:admin_colonies')
            
            # Check if the required column exists
            if 'Colony Name' not in df.columns:
                messages.error(request, 'File must contain a "Colony Name" column.')
                return redirect('custom_admin:admin_colonies')
            
            # Process the data
            success_count = 0
            error_count = 0
            existing_count = 0
            
            for index, row in df.iterrows():
                colony_name = str(row['Colony Name']).strip()
                if colony_name and colony_name != 'nan':
                    # Check if colony already exists
                    if Colony.objects.filter(name__iexact=colony_name).exists():
                        existing_count += 1
                    else:
                        try:
                            Colony.objects.create(name=colony_name)
                            success_count += 1
                        except Exception as e:
                            error_count += 1
            
            # Show results
            if success_count > 0:
                messages.success(request, f'{success_count} colonies imported successfully.')
            if existing_count > 0:
                messages.warning(request, f'{existing_count} colonies already existed and were skipped.')
            if error_count > 0:
                messages.error(request, f'{error_count} colonies failed to import.')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
    
    return redirect('custom_admin:admin_colonies')

# API endpoint for frontend colony search suggestions
def get_colony_suggestions(request):
    query = request.GET.get('q', '')
    colonies = Colony.objects.filter(name__icontains=query).values_list('name', flat=True)[:10]
    return JsonResponse({'colonies': list(colonies)}) 