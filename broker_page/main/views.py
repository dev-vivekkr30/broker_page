import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .forms import BrokerRegistrationForm
from .models import Broker, Colony, Invoice
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .email_utils import send_welcome_email, send_payment_confirmation_email
import os
import tempfile
import shutil
import re
from django.http import HttpResponse
from django.template.loader import render_to_string
import datetime

def home(request):
    colonies = list(Colony.objects.all().order_by('name'))
    return render(request, 'frontend/index.html', {'colonies': colonies})


def agent_registration(request):
    # Clean up any abandoned registration data
    cleanup_abandoned_registration(request)
    
    if request.method == 'POST':
        form = BrokerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Store form data in session instead of saving to database immediately
            form_data = form.cleaned_data.copy()
            
            # Handle file uploads by saving to temporary location
            if form.cleaned_data.get('profile_photo'):
                profile_photo = form.cleaned_data['profile_photo']
                # Save to temporary location
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, profile_photo.name)
                with open(temp_path, 'wb+') as destination:
                    for chunk in profile_photo.chunks():
                        destination.write(chunk)
                form_data['profile_photo_temp_path'] = temp_path
                form_data['profile_photo_name'] = profile_photo.name
                
            if form.cleaned_data.get('profile_video'):
                profile_video = form.cleaned_data['profile_video']
                # Save to temporary location
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, profile_video.name)
                with open(temp_path, 'wb+') as destination:
                    for chunk in profile_video.chunks():
                        destination.write(chunk)
                form_data['profile_video_temp_path'] = temp_path
                form_data['profile_video_name'] = profile_video.name
            
            # Store form data in session
            request.session['registration_data'] = form_data
            
            # Create Razorpay order
            amount = 100000  # ₹1000 in paise
            order_data = {
                'amount': amount,
                'currency': 'INR',
                'receipt': f'broker_{form_data.get("email", "temp")}',
                'payment_capture': '1'
            }
            order = razorpay_client.order.create(order_data)
            
            # Store payment details in session
            request.session['razorpay_order_id'] = order['id']
            
            # Redirect to payment page
            return render(request, 'frontend/payment.html', {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'order_id': order['id'],
                'amount': amount,
                'currency': 'INR',
                'user_data': form_data  # Pass form data to template
            })
        else:
            # Form is invalid, re-render with errors
            return render(request, 'frontend/agent-registration.html', {'form': form})
    else:
        form = BrokerRegistrationForm()
    
    return render(request, 'frontend/agent-registration.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)
        
#         if user is not None:
#             login(request, user)
#             # Redirect to the mobile-specific dashboard URL
#             return redirect('dashboard', mobile=user.mobile)
#         else:
#             # Use a local variable for login error
#             return render(request, 'frontend/login.html', {
#                 'email': email,
#                 'login_error': 'Invalid email or password. Please try again.'
#             })
#     # For GET request, do NOT pass any error or messages context
#     return render(request, 'frontend/login.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            # Check if there's a 'next' parameter for redirection
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                # Default redirect to dashboard using mobile number
                return redirect('dashboard', mobile=user.mobile)
        else:
            return render(request, 'frontend/login.html', {
                'email': email,
                'login_error': 'Invalid email or password. Please try again.'
            })
    return render(request, 'frontend/login.html')

def about(request):
    return render(request, 'frontend/about-us.html')

def search_brokers(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'mobile')
    brokers = Broker.objects.filter(is_staff=False, is_superuser=False)
    if query:
        if search_type == 'mobile':
            brokers = brokers.filter(mobile__icontains=query)
        elif search_type == 'colony':
            brokers = brokers.filter(residence_colony__icontains=query)
    total_brokers = brokers.count()
    context = {
        'brokers': brokers,
        'total_brokers': total_brokers,
        'request': request,
    }
    return render(request, 'frontend/listing-page.html', context)

# Add more views for each page


# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
    
def payment_handler(request):
    print("=" * 50)
    print("DEBUG: Payment handler started")
    print("=" * 50)
    
    if request.method == 'POST':
        # Get payment details from POST data
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        print(f"DEBUG: Payment handler called with payment_id: {razorpay_payment_id}")
        print(f"DEBUG: Order ID: {razorpay_order_id}")
        print(f"DEBUG: Signature: {razorpay_signature}")
        print(f"DEBUG: Session data: {dict(request.session)}")
        
        # Check if all required payment data is present
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            print("DEBUG: Missing payment data")
            print("DEBUG: Redirecting to payment_failed due to missing data")
            messages.error(request, 'Payment data is incomplete. Please try again.')
            return redirect('payment_failed')
        
        print("DEBUG: All payment data present, proceeding with verification")
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            print("DEBUG: Attempting to verify payment signature...")
            razorpay_client.utility.verify_payment_signature(params_dict)
            print("DEBUG: Payment signature verified successfully")
            
            # Get registration data from session
            registration_data = request.session.get('registration_data')
            if not registration_data:
                print("DEBUG: No registration data found in session")
                print("DEBUG: Available session keys:", list(request.session.keys()))
                
                # Try to get order details from Razorpay to verify payment
                try:
                    order_details = razorpay_client.order.fetch(razorpay_order_id)
                    print(f"DEBUG: Order details from Razorpay: {order_details}")
                    
                    # Check if payment was actually made
                    payment_details = razorpay_client.payment.fetch(razorpay_payment_id)
                    print(f"DEBUG: Payment details from Razorpay: {payment_details}")
                    
                    if payment_details.get('status') == 'captured':
                        print("DEBUG: Payment was successful but session data lost")
                        print("DEBUG: Redirecting to payment_failed due to session data loss")
                        messages.error(request, 'Payment was successful but registration data was lost. Please contact support with your payment ID: ' + razorpay_payment_id)
                        return redirect('payment_failed')
                    else:
                        print("DEBUG: Payment not captured")
                        print("DEBUG: Redirecting to payment_failed due to payment not captured")
                        messages.error(request, 'Payment was not completed successfully. Please try again.')
                        return redirect('payment_failed')
                        
                except Exception as e:
                    print(f"DEBUG: Error fetching payment details: {e}")
                    print("DEBUG: Redirecting to agent_registration due to payment details error")
                    messages.error(request, 'Registration data not found. Please try registering again.')
                    return redirect('agent_registration')
            
            print(f"DEBUG: Registration data found, creating user with email: {registration_data.get('email')}")
            
            # Check if user already exists
            existing_user = Broker.objects.filter(email=registration_data['email']).first()
            if existing_user:
                print(f"DEBUG: User already exists with email: {registration_data['email']}")
                print("DEBUG: Redirecting to login due to existing user")
                messages.error(request, 'A user with this email already exists. Please login instead.')
                return redirect('login')
            
            # Check if payment ID has already been used
            existing_payment = Broker.objects.filter(razorpay_payment_id=razorpay_payment_id).first()
            if existing_payment:
                print(f"DEBUG: Payment ID already used: {razorpay_payment_id}")
                print("DEBUG: Redirecting to payment_failed due to duplicate payment")
                messages.error(request, 'This payment has already been processed. Please contact support if you believe this is an error.')
                return redirect('payment_failed')
            
            print("DEBUG: All checks passed, creating user...")
            
            # Create user from session data
            try:
                user = Broker.objects.create_user(
                    email=registration_data['email'],
                    password=registration_data['password1'],
                    full_name=registration_data.get('full_name', '').strip(),
                    company=registration_data.get('company', ''),
                    mobile=registration_data.get('mobile', ''),
                    residence_colony=registration_data.get('residence_colony', ''),
                    office_address=registration_data.get('office_address', ''),
                    about=registration_data.get('about', ''),
                    age=registration_data.get('age'),
                    education=registration_data.get('education', ''),
                    expertise=registration_data.get('expertise', ''),
                    whatsapp=registration_data.get('whatsapp', ''),
                    google_maps_url=registration_data.get('google_maps_url', ''),
                    achievements=registration_data.get('achievements', ''),
                    listings=registration_data.get('listings', ''),
                    min_deal_size=registration_data.get('min_deal_size', ''),
                    max_deal_size=registration_data.get('max_deal_size', ''),
                    facebook_url=registration_data.get('facebook_url', ''),
                    linkedin_url=registration_data.get('linkedin_url', ''),
                    instagram_url=registration_data.get('instagram_url', ''),
                    twitter_url=registration_data.get('twitter_url', ''),
                    youtube_url=registration_data.get('youtube_url', ''),
                    website=registration_data.get('website', ''),
                    is_paid=True,  # Mark as paid immediately
                    razorpay_payment_id=razorpay_payment_id,
                    razorpay_order_id=razorpay_order_id,
                    razorpay_signature=razorpay_signature,
                )
                print(f"DEBUG: User created successfully with ID: {user.id}")
            except Exception as e:
                print(f"DEBUG: Error creating user: {e}")
                import traceback
                traceback.print_exc()
                raise e
            
            # Handle file uploads
            try:
                if 'profile_photo_temp_path' in registration_data:
                    temp_path = registration_data['profile_photo_temp_path']
                    file_name = registration_data['profile_photo_name']
                    # Move file to media directory
                    media_path = os.path.join('profile_photos', file_name)
                    full_media_path = os.path.join(settings.MEDIA_ROOT, media_path)
                    os.makedirs(os.path.dirname(full_media_path), exist_ok=True)
                    shutil.move(temp_path, full_media_path)
                    user.profile_photo = media_path
                    print(f"DEBUG: Profile photo moved to: {media_path}")
                    
                if 'profile_video_temp_path' in registration_data:
                    temp_path = registration_data['profile_video_temp_path']
                    file_name = registration_data['profile_video_name']
                    # Move file to media directory
                    media_path = os.path.join('profile_videos', file_name)
                    full_media_path = os.path.join(settings.MEDIA_ROOT, media_path)
                    os.makedirs(os.path.dirname(full_media_path), exist_ok=True)
                    shutil.move(temp_path, full_media_path)
                    user.profile_video = media_path
                    print(f"DEBUG: Profile video moved to: {media_path}")
                
                user.save()
                print(f"DEBUG: User saved successfully")
            except Exception as e:
                print(f"DEBUG: Error handling file uploads: {e}")
                import traceback
                traceback.print_exc()
                # Don't fail the entire process for file upload issues
                pass
            
            # Send welcome email
            try:
                welcome_sent = send_welcome_email(user)
                if not welcome_sent:
                    print("WARNING: Welcome email failed to send")
            except Exception as e:
                print(f"ERROR: Error sending welcome email: {str(e)}")
            
            # Send payment confirmation email with invoice
            try:
                payment_sent = send_payment_confirmation_email(
                    user=user,
                    payment_id=razorpay_payment_id,
                    order_id=razorpay_order_id,
                    amount=1000  # ₹1000
                )
                if not payment_sent:
                    print("WARNING: Payment confirmation email failed to send")
            except Exception as e:
                print(f"ERROR: Error sending payment confirmation email: {str(e)}")
            
            # Clear session data
            if 'registration_data' in request.session:
                del request.session['registration_data']
            if 'razorpay_order_id' in request.session:
                del request.session['razorpay_order_id']
            
            print("DEBUG: Payment process completed successfully")
            print("DEBUG: Redirecting to thank_you page")
            print("=" * 50)
            # Redirect to thank you page
            return redirect('thank_you')
            
        except razorpay.errors.SignatureVerificationError as e:
            # Specific handling for signature verification errors
            print(f"DEBUG: Razorpay signature verification failed: {e}")
            print("DEBUG: Redirecting to payment_failed due to signature verification error")
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('payment_failed')
            
        except Exception as e:
            # Payment verification failed
            print(f"DEBUG: General exception in payment handler: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            print("DEBUG: Redirecting to payment_failed due to general exception")
            import traceback
            traceback.print_exc()
            
            # Clean up temporary files
            registration_data = request.session.get('registration_data', {})
            if 'profile_photo_temp_path' in registration_data:
                try:
                    os.remove(registration_data['profile_photo_temp_path'])
                    os.rmdir(os.path.dirname(registration_data['profile_photo_temp_path']))
                except:
                    pass
            if 'profile_video_temp_path' in registration_data:
                try:
                    os.remove(registration_data['profile_video_temp_path'])
                    os.rmdir(os.path.dirname(registration_data['profile_video_temp_path']))
                except:
                    pass
            
            # Clear session data on payment failure
            if 'registration_data' in request.session:
                del request.session['registration_data']
            if 'razorpay_order_id' in request.session:
                del request.session['razorpay_order_id']
            return redirect('payment_failed')
    else:
        print("DEBUG: Payment handler called with GET method")
        print("DEBUG: Redirecting to home due to GET method")
    
    return redirect('home')

def thank_you(request):
    print("=" * 50)
    print("DEBUG: thank_you view called")
    print("DEBUG: Request method:", request.method)
    print("DEBUG: User authenticated:", request.user.is_authenticated)
    if request.user.is_authenticated:
        print("DEBUG: User email:", request.user.email)
    print("=" * 50)
    return render(request, 'frontend/thank-you.html')

def payment_failed(request):
    """Handle payment failure and cleanup"""
    print("=" * 50)
    print("DEBUG: payment_failed view called")
    print("DEBUG: Request method:", request.method)
    print("DEBUG: User authenticated:", request.user.is_authenticated)
    print("=" * 50)
    
    # Clean up temporary files
    registration_data = request.session.get('registration_data', {})
    if 'profile_photo_temp_path' in registration_data:
        try:
            os.remove(registration_data['profile_photo_temp_path'])
            os.rmdir(os.path.dirname(registration_data['profile_photo_temp_path']))
            print("DEBUG: Cleaned up profile photo temp file")
        except:
            pass
    if 'profile_video_temp_path' in registration_data:
        try:
            os.remove(registration_data['profile_video_temp_path'])
            os.rmdir(os.path.dirname(registration_data['profile_video_temp_path']))
            print("DEBUG: Cleaned up profile video temp file")
        except:
            pass
    
    # Clear session data
    if 'registration_data' in request.session:
        del request.session['registration_data']
    if 'razorpay_order_id' in request.session:
        del request.session['razorpay_order_id']
    
    print("DEBUG: Session data cleared")
    return render(request, 'frontend/payment-failed.html')

def get_broker_by_mobile(mobile):
    return Broker.objects.filter(mobile=mobile).first()

def generate_profile_slug(full_name, mobile):
    """
    Generate a URL slug from full name and mobile number
    Format: full-name-contact-number
    """
    # Clean the full name: remove special characters, convert to lowercase, replace spaces with hyphens
    name_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', full_name.lower())
    name_slug = re.sub(r'\s+', '-', name_slug.strip())
    
    # Clean the mobile number: remove any non-digit characters
    mobile_clean = re.sub(r'[^\d]', '', mobile)
    
    return f"{name_slug}-{mobile_clean}"

def parse_profile_slug(slug):
    """
    Parse a URL slug to extract mobile number
    Returns the mobile number if found, None otherwise
    """
    # Extract the last part which should be the mobile number
    parts = slug.split('-')
    if len(parts) >= 2:
        # Try to find a mobile number pattern at the end
        mobile_part = parts[-1]
        if mobile_part.isdigit() and len(mobile_part) >= 10:
            return mobile_part
    return None

def get_broker_by_slug(slug):
    """
    Get broker by URL slug (full-name-contact-number format)
    """
    mobile = parse_profile_slug(slug)
    if mobile:
        return Broker.objects.filter(mobile=mobile).first()
    return None

def broker_profile(request, mobile):
    broker = get_broker_by_mobile(mobile)
    if not broker:
        return render(request, 'frontend/404.html', status=404)
    
    print("DEBUG: Broker Profile - User:", broker.email)
    print("DEBUG: Broker Profile - Profile photo field:", broker.profile_photo)
    print("DEBUG: Broker Profile - Profile photo URL:", broker.profile_photo.url if broker.profile_photo else "No photo")
    
    # Calculate expertise_list and listings_list with improved logic
    expertise_list = []
    if broker.expertise and broker.expertise.strip():
        expertise_list = [t.strip() for t in broker.expertise.split(',') if t.strip()]
    
    listings_list = []
    if broker.listings and broker.listings.strip():
        listings_list = [l.strip() for l in broker.listings.split('\n') if l.strip()]
    
    colonies_list = []
    if broker.active_colonies and broker.active_colonies.strip():
        colonies_list = [c.strip() for c in broker.active_colonies.split(',') if c.strip()]
    
    achievements_list = []
    if broker.achievements and broker.achievements.strip():
        achievements_list = [a.strip() for a in broker.achievements.split(',') if a.strip()]
    
    # Create verification status for individual fields
    verification_status = {
        'name': broker.is_name_verified,
        'photo': broker.is_photo_verified,
        'company': broker.is_company_verified,
        'age': broker.is_age_verified,
        'education': broker.is_education_verified,
        'residence': broker.is_residence_colony_verified,
        'office': broker.is_office_address_verified,
    }
    
    context = {
        'broker': broker,
        'is_verified': broker.is_fully_verified,
        'verification_status': verification_status,
        'expertise_list': expertise_list,
        'listings_list': listings_list,
        'colonies_list': colonies_list,
        'achievements_list': achievements_list,
        'request': request,
    }
    return render(request, 'frontend/broker-profile.html', context)

@login_required(login_url='/login/')
def dashboard(request, mobile):
    if request.user.mobile != mobile:
        messages.error(request, 'You do not have permission to access this dashboard.')
        return redirect('home')
    broker = request.user
    print("DEBUG: Dashboard - User:", broker.email)
    print("DEBUG: Dashboard - Profile photo field:", broker.profile_photo)
    print("DEBUG: Dashboard - Profile photo URL:", broker.profile_photo.url if broker.profile_photo else "No photo")
    
    # Calculate expertise_list and listings_list with improved logic
    expertise_list = []
    if broker.expertise and broker.expertise.strip():
        expertise_list = [t.strip() for t in broker.expertise.split(',') if t.strip()]
    
    listings_list = []
    if broker.listings and broker.listings.strip():
        listings_list = [l.strip() for l in broker.listings.split('\n') if l.strip()]
    
    # Split active_colonies for display
    colonies_list = []
    if broker.active_colonies and broker.active_colonies.strip():
        colonies_list = [c.strip() for c in broker.active_colonies.split(',') if c.strip()]
    
    achievements_list = []
    if broker.achievements and broker.achievements.strip():
        achievements_list = [a.strip() for a in broker.achievements.split(',') if a.strip()]
    
    print("DEBUG: Dashboard - Expertise field:", repr(broker.expertise))
    print("DEBUG: Dashboard - Expertise list:", expertise_list)
    print("DEBUG: Dashboard - Listings field:", repr(broker.listings))
    print("DEBUG: Dashboard - Listings list:", listings_list)
    
    # More comprehensive profile completion calculation
    profile_fields = [
        'full_name', 'company', 'mobile', 'residence_colony', 'office_address',
        'about', 'age', 'education', 'expertise', 'whatsapp', 'achievements',
        'listings', 'min_deal_size', 'max_deal_size', 'facebook_url', 'linkedin_url',
        'instagram_url', 'twitter_url', 'youtube_url', 'website', 'profile_photo'
    ]
    
    filled_fields = 0
    for field in profile_fields:
        value = getattr(broker, field)
        if value:
            # For string fields, check if not empty after stripping
            if isinstance(value, str) and value.strip():
                filled_fields += 1
            # For non-string fields (like age), check if truthy
            elif not isinstance(value, str):
                filled_fields += 1
    
    profile_percentage = int((filled_fields / len(profile_fields)) * 100)
    
    print("DEBUG: Dashboard - Filled fields:", filled_fields, "out of", len(profile_fields))
    print("DEBUG: Dashboard - Profile percentage:", profile_percentage)
    
    verification_status = {
        'name': broker.is_name_verified,
        'photo': broker.is_photo_verified,
        'company': broker.is_company_verified,
        'age': broker.is_age_verified,
        'education': broker.is_education_verified,
        'residence': broker.is_residence_colony_verified,
        'office': broker.is_office_address_verified,
    }
    context = {
        'broker': broker,
        'profile_percentage': profile_percentage,
        'is_verified': broker.is_fully_verified,
        'verification_status': verification_status,
        'expertise_list': expertise_list,
        'listings_list': listings_list,
        'colonies_list': colonies_list,
        'achievements_list': achievements_list,
    }
    return render(request, 'frontend/broker-dashboard.html', context)

@login_required(login_url='/login/')
def edit_profile(request):
    broker = request.user
    all_colonies = list(Colony.objects.all().order_by('name'))
    selected_colonies = []
    if broker.active_colonies and broker.active_colonies.strip():
        selected_colonies = [c.strip() for c in broker.active_colonies.split(',') if c.strip()]

    if request.method == 'POST':
        # Update broker fields from POST data
        broker.full_name = request.POST.get('full_name', broker.full_name)
        broker.age = request.POST.get('age', broker.age)
        broker.education = request.POST.get('education', broker.education)
        broker.residence_colony = request.POST.get('residence_colony', broker.residence_colony)
        broker.about = request.POST.get('about', broker.about)
        broker.email = request.POST.get('email', broker.email)
        broker.mobile = request.POST.get('mobile', broker.mobile)
        broker.whatsapp = request.POST.get('whatsapp', broker.whatsapp)
        broker.company = request.POST.get('company', broker.company)
        broker.office_address = request.POST.get('office_address', broker.office_address)
        broker.google_maps_url = request.POST.get('google_maps_url', broker.google_maps_url)
        broker.expertise = request.POST.get('expertise', broker.expertise)
        broker.min_deal_size = request.POST.get('min_deal_size', broker.min_deal_size)
        broker.max_deal_size = request.POST.get('max_deal_size', broker.max_deal_size)
        broker.achievements = request.POST.get('achievements', broker.achievements)
        # Handle multiple listings
        listings = request.POST.getlist('listings')
        broker.listings = '\n'.join([l.strip() for l in listings if l.strip()])
        broker.facebook_url = request.POST.get('facebook_url', broker.facebook_url)
        broker.linkedin_url = request.POST.get('linkedin_url', broker.linkedin_url)
        broker.instagram_url = request.POST.get('instagram_url', broker.instagram_url)
        broker.twitter_url = request.POST.get('twitter_url', broker.twitter_url)
        broker.youtube_url = request.POST.get('youtube_url', broker.youtube_url)
        broker.website = request.POST.get('website', broker.website)
        # Colonies (multi-select)
        colonies = request.POST.getlist('colonies')
        broker.active_colonies = ', '.join(colonies)
        # Handle file uploads
        if 'profile_photo' in request.FILES:
            broker.profile_photo = request.FILES['profile_photo']
        if 'profile_video' in request.FILES:
            broker.profile_video = request.FILES['profile_video']
        if 'company_logo' in request.FILES:
            broker.company_logo = request.FILES['company_logo']
        if 'personal_document' in request.FILES:
            broker.personal_document = request.FILES['personal_document']
        if 'education_document' in request.FILES:
            broker.education_document = request.FILES['education_document']
        if 'company_document' in request.FILES:
            broker.company_document = request.FILES['company_document']
        broker.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')

    # Fetch invoices from the database
    invoices = Invoice.objects.filter(broker=broker).order_by('-end_date')
    # Next payment due is the end_date of the latest invoice, or None
    next_payment_due = invoices.first().end_date if invoices.exists() else None

    # Calculate can_renew: True if next_payment_due is within 30 days or overdue
    import datetime
    can_renew = False
    if next_payment_due:
        today = datetime.date.today()
        days_until_due = (next_payment_due - today).days
        can_renew = days_until_due <= 30

    # Prepare listings_list for template
    listings_list = []
    if broker.listings and broker.listings.strip():
        listings_list = [l.strip() for l in broker.listings.split('\n') if l.strip()]

    context = {
        'broker': broker,
        'all_colonies': all_colonies,
        'selected_colonies': selected_colonies,
        'invoices': invoices,
        'next_payment_due': next_payment_due,
        'can_renew': can_renew,
        'listings_list': listings_list,
    }
    return render(request, 'frontend/edit-profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

def payment_cancelled(request):
    """Handle payment cancellation and cleanup"""
    print("DEBUG: Payment cancelled view called")
    
    # Clean up temporary files
    registration_data = request.session.get('registration_data', {})
    if 'profile_photo_temp_path' in registration_data:
        try:
            os.remove(registration_data['profile_photo_temp_path'])
            os.rmdir(os.path.dirname(registration_data['profile_photo_temp_path']))
            print("DEBUG: Cleaned up profile photo temp file")
        except:
            pass
    if 'profile_video_temp_path' in registration_data:
        try:
            os.remove(registration_data['profile_video_temp_path'])
            os.rmdir(os.path.dirname(registration_data['profile_video_temp_path']))
            print("DEBUG: Cleaned up profile video temp file")
        except:
            pass
    
    # Clear session data
    if 'registration_data' in request.session:
        del request.session['registration_data']
    if 'razorpay_order_id' in request.session:
        del request.session['razorpay_order_id']
    
    print("DEBUG: Session data cleared")
    return redirect('payment_failed')

def cleanup_abandoned_registration(request):
    """Clean up abandoned registration data from session"""
    registration_data = request.session.get('registration_data', {})
    if registration_data:
        # Clean up temporary files
        if 'profile_photo_temp_path' in registration_data:
            try:
                os.remove(registration_data['profile_photo_temp_path'])
                os.rmdir(os.path.dirname(registration_data['profile_photo_temp_path']))
            except:
                pass
        if 'profile_video_temp_path' in registration_data:
            try:
                os.remove(registration_data['profile_video_temp_path'])
                os.rmdir(os.path.dirname(registration_data['profile_video_temp_path']))
            except:
                pass
        
        # Clear session data
        if 'registration_data' in request.session:
            del request.session['registration_data']
        if 'razorpay_order_id' in request.session:
            del request.session['razorpay_order_id']

def contact_us(request):
    return render(request, 'frontend/contact-us.html')

def privacy_policy(request):
    return render(request, 'frontend/privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'frontend/terms-and-conditions.html')

def refund_policy(request):
    return render(request, 'frontend/refund-policy.html')

@login_required
def download_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, broker=request.user)
    html = render_to_string('admin/invoice.html', {'broker': invoice.broker, 'invoice': invoice})
    try:
        from weasyprint import HTML
        pdf = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response
    except ImportError:
        return HttpResponse(html)

@login_required(login_url='/login/')
def renew_plan(request):
    broker = request.user
    amount = 100000  # ₹1000 in paise
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'renewal_{broker.email}_{broker.id}',
        'payment_capture': '1'
    }
    order = razorpay_client.order.create(order_data)
    request.session['renewal_order_id'] = order['id']
    request.session['renewal_amount'] = amount
    return render(request, 'frontend/payment.html', {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': amount,
        'currency': 'INR',
        'user_data': {'email': broker.email, 'full_name': broker.full_name}
    })

@login_required(login_url='/login/')
def payment_handler_renewal(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        broker = request.user
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            messages.error(request, 'Payment data is incomplete. Please try again.')
            return redirect('payment_failed')
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            # Create new invoice for renewal
            from datetime import timedelta
            last_invoice = Invoice.objects.filter(broker=broker).order_by('-end_date').first()
            start_date = last_invoice.end_date if last_invoice else broker.date_joined.date()
            end_date = start_date + timedelta(days=365)
            invoice_number = f"INV-{broker.id}-{end_date.strftime('%Y%m%d')}"
            amount = request.session.get('renewal_amount', 100000) / 100.0
            invoice = Invoice.objects.create(
                broker=broker,
                start_date=start_date,
                end_date=end_date,
                amount=amount,
                invoice_number=invoice_number
            )
            # Update broker's plan_end_date
            broker.plan_end_date = end_date
            broker.save()
            # Optionally, store payment IDs
            broker.razorpay_payment_id = razorpay_payment_id
            broker.razorpay_order_id = razorpay_order_id
            broker.razorpay_signature = razorpay_signature
            broker.save()
            # Clean up session
            if 'renewal_order_id' in request.session:
                del request.session['renewal_order_id']
            if 'renewal_amount' in request.session:
                del request.session['renewal_amount']
            messages.success(request, 'Renewal successful!')
            return redirect('edit_profile')
        except Exception as e:
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('payment_failed')
    return redirect('home')