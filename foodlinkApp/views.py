from django.shortcuts import render, redirect
from django.db.models import Sum # Import the Sum aggregator at the top
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import FoodDonation, CustomUser, ContactMessage

# Decorator to enforce custom role access control
def role_required(allowed_roles):
    def decorator(view_func):
        @login_required(login_url='login')
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                is_admin = request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'ADMIN')
                if is_admin or (hasattr(request.user, 'role') and request.user.role in allowed_roles):
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Access Denied: You do not have the required role to view this page.")
        return _wrapped_view
    return decorator


# ==========================================
# 1. PUBLIC PAGES
# ==========================================

def home_view(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        partner_type = request.POST.get('partner_type')
        message = request.POST.get('message')
        
        if name and email and partner_type and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                partner_type=partner_type,
                message=message
            )
            return render(request, 'contact.html', {'success': True})
            
    return render(request, 'contact.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirect to the appropriate portal depending on user role
            if user.is_superuser or user.role == 'ADMIN':
                return redirect('master-admin')
            elif user.role == 'DONOR':
                return redirect('donor-dashboard')
            elif user.role == 'NGO':
                return redirect('ngo-dashboard')
            elif user.role == 'VOLUNTEER':
                return redirect('volunteer')
        else:
            return render(request, 'login.html', {'error': 'Invalid email/username or password.'})

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if username and password and role:
            if CustomUser.objects.filter(username=username).exists():
                return render(request, 'register.html', {'error': 'Username/Email already registered.'})
            
            # Create user using Django's create_user (hashes password securely)
            CustomUser.objects.create_user(
                username=username,
                password=password,
                role=role
            )
            return redirect('login')
        else:
            return render(request, 'register.html', {'error': 'All fields are required.'})
            
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# 2. DONOR DASHBOARD (With Form Storage)
# ==========================================

@role_required(['DONOR'])
def donor_dashboard_view(request):
    user = request.user
    if user and not user.first_name:
        user.first_name = user.username.split('@')[0].capitalize()

    # Process frontend form data if submitted via POST
    if request.method == 'POST':
        food_type = request.POST.get('food_type')
        quantity_kg_raw = request.POST.get('quantity_kg')
        expiry_hours = request.POST.get('expiry_hours')
        
        # Safely convert to integer to prevent server errors on empty or invalid input
        try:
            quantity_kg = int(quantity_kg_raw) if quantity_kg_raw else 0
        except (ValueError, TypeError):
            quantity_kg = 0

        # Save straight to our database model
        FoodDonation.objects.create(
            food_type=food_type,
            quantity_kg=quantity_kg,
            expiry_hours=expiry_hours,
            status='LISTED'
        )
        # Redirect back to the clean dashboard URL pattern
        return redirect('donor-dashboard')

    # Fetch live database records to render on the dashboard pipeline stream
    all_donations = FoodDonation.objects.all().order_by('-created_at')
    
    # Calculate dynamic total sum (Ex: 89kg + 45kg = 134kg)
    # If the database is empty, it defaults to 0
    total_kg_dict = FoodDonation.objects.aggregate(Sum('quantity_kg'))
    dynamic_total = total_kg_dict['quantity_kg__sum'] or 0
    
    # Fetch active counts from our database models
    active_pickups_count = FoodDonation.objects.filter(status='ASSIGNED').count()
    partner_ngos_count = CustomUser.objects.filter(role='NGO').count()

    context = {
        'user': user,
        'total_rescued': f"{dynamic_total}kg",
        'impact_rank': "#1", # Logic for ranking users can be implemented later
        'active_pickups': active_pickups_count,
        'partner_ngos': partner_ngos_count,
        'donations': all_donations, 
    }
    return render(request, 'donor-dashboard.html', context)


@role_required(['DONOR'])
def delete_donation_view(request, donation_id):
    if request.method == 'POST':
        try:
            donation = FoodDonation.objects.get(id=donation_id)
            donation.delete()
        except FoodDonation.DoesNotExist:
            pass
    return redirect('donor-dashboard')


# ==========================================
# 3. NGO & VOLUNTEER DASHBOARDS
# ==========================================

@role_required(['NGO'])
def ngo_dashboard_view(request):
    all_donations = FoodDonation.objects.all().order_by('-created_at')
    
    context = {
        'ngo_name': "Akshaya Care Trust",
        'region': "South Delhi",
        'active_volunteers': 62,
        'donations': all_donations,
    }
    return render(request, 'ngo-dashboard.html', context)


@role_required(['NGO'])
def accept_donation_view(request, donation_id):
    if request.method == 'POST':
        try:
            donation = FoodDonation.objects.get(id=donation_id)
            if donation.status == 'LISTED':
                donation.status = 'ASSIGNED'
                donation.save()
        except FoodDonation.DoesNotExist:
            pass
    return redirect('ngo-dashboard')


@role_required(['VOLUNTEER'])
def volunteer_dashboard_view(request):
    return render(request, 'volunteer.html')

#========================================================

from django.http import HttpResponseForbidden

def master_admin_view(request):
    # Security Guard: Block any user who isn't a logged-in Django Superuser or Admin role
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
        return HttpResponseForbidden("Access Denied: This control center is restricted to platform administrators.")

    # Gather global cross-platform datasets
    all_donations = FoodDonation.objects.all().order_by('-created_at')
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    all_users = CustomUser.objects.all().order_by('-date_joined')
    
    # Calculate global platform performance statistics
    total_listings = all_donations.count()
    claimed_donations = all_donations.filter(status='ASSIGNED')
    total_claimed = claimed_donations.count()
    
    total_weight = all_donations.aggregate(Sum('quantity_kg'))['quantity_kg__sum'] or 0
    total_messages = contact_messages.count()
    
    total_users = all_users.count()
    total_admins = all_users.filter(role='ADMIN').count()
    total_donors = all_users.filter(role='DONOR').count()
    total_ngos = all_users.filter(role='NGO').count()
    total_volunteers = all_users.filter(role='VOLUNTEER').count()

    context = {
        'donations': all_donations,
        'contact_messages': contact_messages,
        'users': all_users,
        'total_listings': total_listings,
        'total_claimed': total_claimed,
        'total_weight': f"{total_weight} kg",
        'total_messages': total_messages,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_donors': total_donors,
        'total_ngos': total_ngos,
        'total_volunteers': total_volunteers,
    }
    return render(request, 'master-admin.html', context)


def delete_message_view(request, message_id):
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
        return HttpResponseForbidden("Access Denied: You do not have permission to perform this action.")
    
    if request.method == 'POST':
        try:
            msg = ContactMessage.objects.get(id=message_id)
            msg.delete()
        except ContactMessage.DoesNotExist:
            pass
    return redirect('master-admin')


def toggle_user_status_view(request, user_id):
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
        return HttpResponseForbidden("Access Denied: You do not have permission to perform this action.")
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            if user == request.user:
                # Can't deactivate yourself
                pass
            else:
                user.is_active = not user.is_active
                user.save()
        except CustomUser.DoesNotExist:
            pass
    return redirect('master-admin')


def delete_user_view(request, user_id):
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
        return HttpResponseForbidden("Access Denied: You do not have permission to perform this action.")
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            if user == request.user:
                # Can't delete yourself
                pass
            else:
                user.delete()
        except CustomUser.DoesNotExist:
            pass
    return redirect('master-admin')


def change_user_role_view(request, user_id):
    if not request.user.is_authenticated or not (request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'):
        return HttpResponseForbidden("Access Denied: You do not have permission to perform this action.")
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            new_role = request.POST.get('role')
            if new_role in ['DONOR', 'NGO', 'VOLUNTEER', 'ADMIN']:
                user.role = new_role
                if new_role == 'ADMIN':
                    user.is_staff = True
                else:
                    if user.is_superuser:
                        user.role = 'ADMIN'  # Keep ADMIN for superuser
                    else:
                        user.is_staff = False
                user.save()
        except CustomUser.DoesNotExist:
            pass
    return redirect('master-admin')


# ==========================================
# 4. GEMINI CHAT API BACKEND
# ==========================================

import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def gemini_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not user_message:
        return JsonResponse({'error': 'Message is empty'}, status=400)
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Programmatically look for a local .env file in the project base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(base_dir, '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key_part, val_part = line.split('=', 1)
                                if key_part.strip() == 'GEMINI_API_KEY':
                                    api_key = val_part.strip().strip('"').strip("'")
                                    break
            except Exception:
                pass

    if not api_key:
        # Fallback responses to keep the application functional and testable without a key
        mock_replies = {
            "hello": "Hello! I am your FoodLink Assistant. How can I help you today?",
            "hi": "Hi there! I am the FoodLink Assistant. How can I help you today?",
            "help": "I can help you list food donations, find volunteer opportunities, or answer questions about FoodLink.",
            "volunteer": "To volunteer, please click on 'Volunteer Portal' in the navigation menu above to register and find active claims.",
            "donate": "To donate surplus food, please head to the 'Donor Portal' in the navigation menu to list your food items.",
            "ngo": "NGOs can view available surplus food listings and manage distributions through the 'NGO Portal' in the navigation menu."
        }
        
        msg_lower = user_message.lower()
        reply = None
        for key, val in mock_replies.items():
            if key in msg_lower:
                reply = val
                break
        
        if not reply:
            reply = f"Thank you for your message: '{user_message}'. To unlock full AI-powered assistant capabilities, please configure the GEMINI_API_KEY environment variable on the server."
            
        return JsonResponse({'reply': reply})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [
            {
                "parts": [{"text": user_message}]
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are FoodLink Assistant, a helpful, polite, and professional AI chatbot integrated into "
                        "the FoodLink platform. FoodLink connects surplus food donors (restaurants, caterers, etc.) "
                        "with NGOs and volunteer transporters. Help the user understand how they can list surplus food, "
                        "claim transport routes, or register. Keep responses friendly, structured, concise, and focused "
                        "on FoodLink. Avoid repeating the user's prompt."
                    )
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response_data = response.json()
        
        if response.status_code == 200:
            try:
                candidate = response_data['candidates'][0]
                reply_text = candidate['content']['parts'][0]['text']
                return JsonResponse({'reply': reply_text})
            except (KeyError, IndexError):
                return JsonResponse({'reply': "Sorry, I received an invalid response structure from the Gemini API."}, status=500)
        else:
            error_message = response_data.get('error', {}).get('message', 'Unknown API error')
            return JsonResponse({'reply': f"Gemini API Error: {error_message}"}, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({'reply': f"Failed to connect to Gemini API: {str(e)}"}, status=500)
