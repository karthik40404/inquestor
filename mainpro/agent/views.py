from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from .models import *
import random,string
from django.conf import settings
from django.http import JsonResponse
import json
# Create your views here.

def landing_page(req):
    if 'admin' in req.session:
        return redirect('admdash')  # Redirect admin
    if 'agent' in req.session:
        return redirect('agent_dashboard')  # Redirect agent
    if 'user' in req.session:
        return redirect('user_home')  # Redirect user
    
    case_categories = CaseCategory.objects.all()
    return render(req, 'landing_page.html',{'case_categories': case_categories})  # Show landing page


def log(req):
    if req.session.get('role') == 'admin':
        return redirect(admdash)
    if req.session.get('role') == 'agent':
        return redirect(agent_dashboard)
    if req.session.get('role') == 'user':
        return redirect(user_home)

    if req.method == 'POST':
        email = req.POST['email']
        psw = req.POST['psw']
        data = authenticate(username=email, password=psw)

        if data:
            req.session.flush()  # Clear previous session
            login(req, data)

            # Determine user role
            if data.is_superuser:
                req.session['role'] = 'admin'
                req.session['user_id'] = data.id
                return redirect(admdash)
            elif data.is_staff:
                req.session['role'] = 'agent'
                req.session['user_id'] = data.id
                return redirect(agent_dashboard)
            else:
                req.session['role'] = 'user'
                req.session['user_id'] = data.id
                return redirect(user_home)
        else:
            messages.warning(req, "Incorrect username or password.")
            return render(req, 'login.html', {'error': 'Incorrect username or password.'})

    return render(req, 'login.html')

def lout(req):
    logout(req)
    return redirect('log')

def reg(req):
    if req.method=="POST":
        name=req.POST['name']
        email=req.POST['email']
        psw=req.POST['psw']
        data=User.objects.create_user(first_name=name,email=email,username=email,password=psw)
        data.save()
        return redirect(log)
    else:
        return render(req,'userreg.html')

def admdash(req):
    cases = Case.objects.all()
    agents = Agent.objects.all()
    clients = User.objects.all()
    categories = CaseCategory.objects.all()
    return render(req, 'admin/admindash.html', {'cases': cases,'agents': agents,'clients': clients,'categories': categories,})

def generate_random_password(length=8):
    """Generate a random alphanumeric password."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_agent(req):
    if req.method == 'POST':
        username = req.POST['username']
        email = req.POST['email']
        phone = req.POST['phone']
        address = req.POST['address']

        if User.objects.filter(username=username).exists():
            messages.error(req, f"The username '{username}' is already taken.")
            return redirect('add_agent')
        if User.objects.filter(email=email).exists():
            messages.error(req, f"The email '{email}' is already in use.")
            return redirect('add_agent')
        # Generate a random password
        random_password = generate_random_password()
        user = User.objects.create_user(username=username, email=email, is_staff=True, password=random_password)
        user.save()

        # Create agent profile
        agent = Agent.objects.create(
            user=user,
            name=username,
            phone=phone,
            address=address,
            is_active=True
        )
        agent.save()

        # Send email with the random password
        try:
            send_mail(
                subject="Welcome to Detective Management System",
                message=f"Hi {username},\n\nYour account has been created. Here are your login details:\n\n"
                        f"Username: {username}\nPassword: {random_password}\n\nPlease log in and change your password as soon as possible.",
                from_email="karthik.kalarimadom@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(req, 'Agent added successfully, and login details sent to their email!')
        except Exception as e:
            messages.error(req, f"Agent added, but email could not be sent. Error: {e}")  
        return redirect(admdash)
    return render(req, 'admin/add_agent.html')

def delete_agent(req, agent_id):
    # Ensure that the user is an admin
    if not req.user.is_staff:
        messages.error(req, "You do not have permission to delete an agent.")
        return redirect('admin_dashboard')  # Redirect to the admin dashboard if no permission
    
    agent = get_object_or_404(Agent, id=agent_id)
    
    # Delete the agent and associated user if necessary
    user = agent.user  # Assuming there's a related user model for agent
    agent.delete()  # Delete the agent
    user.delete()  # Delete the user account if needed

    messages.success(req, f'Agent {agent.user.username} has been deleted successfully.')
    return redirect(admdash)

def add_case_category(req):
    if req.method == 'POST':
        c_name = req.POST.get('c_name')  # Using .get() to avoid KeyError if the field is missing
        c_image = req.FILES.get('c_image')  # Accessing file data
        c_disc = req.POST.get('c_disc')  # Using .get() for safety

        # Check if the required fields are present
        if c_name and c_image and c_disc:
            # Create the category object
            category = CaseCategory.objects.create(
                c_name=c_name,
                c_image=c_image,
                c_disc=c_disc
            )
            category.save()
            messages.success(req, 'Category added successfully!')
        else:
            # Handle missing fields
            if not c_name:
                messages.error(req, 'Category name is required.')
            if not c_image:
                messages.error(req, 'Please upload an image for the category.')
            if not c_disc:
                messages.error(req, 'Description is required.')

        return redirect(admdash)  
    return render(req, 'admin/add_case_category.html')

def list_cases(req):
    cases = Case.objects.all()
    return render(req, 'admin/list_cases.html', {
        'cases': cases
    })

def case_details(req, case_id):
    case = get_object_or_404(Case, id=case_id)
    return render(req, 'admin/case_details.html', {
        'case': case
    })

def list_clients(req):
    clients = User.objects.all()
    return render(req, 'admin/list_clients.html', {
        'clients': clients
    })

def agent_dashboard(req):
    # Get the agent associated with the current user
    agent = Agent.objects.filter(user=req.user).first()

    # Get cases associated with this agent
    cases = Case.objects.filter(agent=agent)

    # Fetch chat messages for all the agent's cases
    cases_data = []
    for case in cases:
        chat_messages = ChatMessage.objects.filter(case=case).order_by('timestamp')
        cases_data.append({
            'case': case,
            'chat_messages': chat_messages,
        })

    # Count the total, open, and closed cases
    total_cases = cases.count()
    open_cases = cases.filter(status='Open').count()
    closed_cases = cases.filter(status='Closed').count()

    return render(req, 'agent/agent_dashboard.html', {
        'cases_data': cases_data,
        'total_cases': total_cases,
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        'agent': agent,  # You can use 'agent' directly, no need for req.user here
    })

def change_password(req):
    if req.method == 'POST':
        current_password = req.POST.get('current_password')  # Use .get() instead of direct access
        new_password = req.POST.get('new_password')
        confirm_password = req.POST.get('confirm_password')

        # Ensure that new password and confirm password match
        if new_password != confirm_password:
            messages.error(req, "New passwords do not match.")
            return redirect('change_password')  # Replace with the actual name of your URL pattern

        # Authenticate the user with current password
        user = authenticate(req, username=req.user.username, password=current_password)
        if user is not None:
            # If user is authenticated, set the new password
            user.set_password(new_password)
            user.save()

            # Keep the user logged in with the updated password
            update_session_auth_hash(req, user)
            messages.success(req, "Your password has been changed successfully!")
            return redirect('agent_dashboard')  # Replace with the actual URL name for the agent dashboard
        else:
            messages.error(req, "Current password is incorrect.")
            return redirect('change_password')  # Redirect back to the password change page
    return render(req, 'agent/change_password.html')

def update_case_status(req, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    if req.method == 'POST':
        status = req.POST['status']
        case.status = status
        case.save()
        messages.success(req, 'Case status updated successfully!')
        return redirect(agent_dashboard)
    
    return render(req, 'agent/update_case_status.html', {
        'case': case
    })

def cases_by_category(req, category_id):
    category = get_object_or_404(CaseCategory, id=category_id)

    cases = Case.objects.filter(category=category)
    
    return render(req, 'cases_by_category.html', {
        'category': category,
        'cases': cases,
    })

def user_home(req):
    categories = CaseCategory.objects.all() 
    agents = Agent.objects.all()
    return render(req, 'client/userhome.html', {'categories': categories,'agents': agents})

def submit_case(req, category_id):
    category = get_object_or_404(CaseCategory, id=category_id)
    agents = Agent.objects.filter(is_active=True)

    if req.method == 'POST':
        title= req.POST.get('title')
        description = req.POST.get('details')
        agent_id = req.POST.get('agent')
        user_id = req.POST.get('user')
        evidence_file = req.FILES.get('evidence')
        evidence_description = req.POST.get('evidence_description')

        if not req.user.is_authenticated:
            messages.error(req, "You need to log in to submit a case.")
            return redirect('log')

        if title and description and agent_id and evidence_file and evidence_description:
            try:
                
                agent = get_object_or_404(Agent, id=agent_id)
                user = get_object_or_404(User, id=user_id)       
            
                case = Case.objects.create(
                    agent=agent,
                    case_category=category,  
                    case_detail=description,
                    evidence=evidence_file,
                    evidence_details=evidence_description,
                    user=user,
                    status='open',  
                )
                
                send_mail(
                    subject=f"New Case Assigned:{case.title}",
                    message=f"A new case has been assigned to you.\n\n"
                            f"Category: {category.c_name}\n"
                            f"Description: {case.case_detail}\n"
                            f"Please log in for more details.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[agent.user.email],
                )
                messages.success(req, "Case submitted successfully.")
                return redirect('user_home')  
            except Exception as e:
                messages.error(req, "An error occurred while submitting the case.")
                print(str(e))  
        else:
            messages.error(req, "All fields are required.") 
    return render(req, 'client/submitcase.html', {'category': category, 'agents': agents})
    
def chat_case(request, case_id):
    case = get_object_or_404(Case, id=case_id)  # Use get_object_or_404 for better error handling
    chat_messages = ChatMessage.objects.filter(case=case).order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            sender = request.user
            ChatMessage.objects.create(
                case=case,
                sender=sender,
                message=message
            )
            # After sending the message, redirect to the same page to avoid resubmission on refresh
            return redirect('chat_case', case_id=case.id)

    return render(request, 'chat_case.html', {
        'case': case,
        'chat_messages': chat_messages,
    })

def send_message(req, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    if req.method == 'POST' and req.user.is_authenticated:
        message_content = req.POST.get('message')
        if message_content:
            ChatMessage.objects.create(
                case=case,
                sender=req.user,
                message=message_content,
            )
            return redirect(agent_dashboard)  # Redirect to the same page or case page

    return redirect(agent_dashboard)

def agent_profile(req, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    cases = Case.objects.filter(agent=agent)

    # Fetch chat messages for each case and add it to the context
    cases_data = []
    for case in cases:
        chat_messages = ChatMessage.objects.filter(case=case).order_by('timestamp')
        cases_data.append({
            'case': case,
            'chat_messages': chat_messages,
        })

    return render(req, 'agent/agent_profile.html', {
        'agent': agent,
        'cases_data': cases_data,
    })


def contact_page(req):
    return render(req,'contact_page.html')

def message(req):
    if req.method=='POST':
          name=req.POST['name']
          email=req.POST['email']
          message=req.POST['message']
          data=Message.objects.create(name=name,email=email,message=message)
          data.save()
          return redirect(contact_page)
    else:
        return render(req,'contact_page.html')
    
def agent_case_details(req, case_id):
    case = get_object_or_404(Case, id=case_id)
    if req.user != case.agent.user:
        messages.error(req, "You do not have permission to view this case.")
        return redirect('user_home')

    return render(req, 'agent/case_details.html', {
        'case': case
    })