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
    # Redirect based on session roles
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
    clients = Client.objects.all()
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
        
        # Generate a random password
        random_password = generate_random_password()
        
        # Create the user first
        user = User.objects.create_user(username=username, email=email, is_staff=True)
        user.set_password(random_password) 
        user.save()
        
        # Create agent profile
        agent = Agent.objects.create(
            user=user,
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

def add_case_category(req):
    if req.method == 'POST':
        c_name = req.POST['c_name']
        c_image = req.FILES.get('c_image')
        description = req.POST['description']
        if c_image:
            category = CaseCategory.objects.create(
                c_name=c_name,
                c_image=c_image,
                description=description
            )
            category.save()
            messages.success(req, 'Category added successfully!')
        else:
            messages.error(req, 'Please upload an image for the category.') 
        return redirect(admdash) 
    return render(req, 'admin/add_case_category.html')

def add_case(req):
    if req.method == 'POST':
        title = req.POST['title']
        description = req.POST['description']
        client_id = req.POST['client']
        category_id = req.POST['category']
        assigned_agent_id = req.POST['assigned_agent']
        
        # Fetch objects for client, category, and agent
        client = Client.objects.get(id=client_id)
        category = CaseCategory.objects.get(id=category_id)
        agent = Agent.objects.get(id=assigned_agent_id) if assigned_agent_id else None
        
        # Create the case
        case = Case.objects.create(
            title=title,
            description=description,
            client=client,
            assigned_agent=agent,
            status='Open',
            category=category
        )
        case.save()
        messages.success(req, "Case added successfully!")
        return redirect(admdash)  # Redirect back to the admin dashboard

    clients = Client.objects.all()
    agents = Agent.objects.all()
    categories = CaseCategory.objects.all()
    return render(req, 'admin/add_case.html', {
        'clients': clients,
        'agents': agents,
        'categories': categories,
    })

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
    clients = Client.objects.all()
    return render(req, 'admin/list_clients.html', {
        'clients': clients
    })

def agent_dashboard(req):
    # Get the agent associated with the current user, handle case where no agent is found
    agent = Agent.objects.filter(user=req.user).first()
    
    if not agent:
        # Use Django's messages module for error notification
        messages.error(req, "Agent not found. Please check your account details.")
        return redirect(agent_dashboard)  # Redirect to an error page or handle appropriately

    # Get the cases assigned to this agent
    cases = Case.objects.filter(assigned_agent=req.user)


    # Count the total, open, and closed cases
    total_cases = cases.count()
    open_cases = cases.filter(status='Open').count()
    closed_cases = cases.filter(status='Closed').count()

    # Prepare cases data with associated chat messages
    cases_data = []
    for case in cases:
        case_messages = ChatMessage.objects.filter(case=case)  # Renamed 'messages' to 'case_messages'
        cases_data.append({
            'case': case,
            'messages': case_messages,
        })

    # Render the dashboard with the necessary data
    return render(req, 'agent/agent_dashboard.html', {
        'cases_data': cases_data,
        'total_cases': total_cases,
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        'agent': req.user,
    })

def change_password(req):
    if req.method == 'POST':
        current_password = req.POST['current_password']
        new_password = req.POST['new_password']
        confirm_password = req.POST['confirm_password']
        
        if new_password != confirm_password:
            messages.error(req, "New passwords do not match.")
            return redirect('change_password')  
        
        user = authenticate(req, username=req.user.username, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            
            update_session_auth_hash(req, user)
            messages.success(req, "Your password has been changed successfully!")
            return redirect(agent_dashboard)  
        else:
            messages.error(req, "Current password is incorrect.")
            return redirect(change_password)
    
    return render(req, 'agent/change_password.html')

def add_client(req):
    if req.method == 'POST':
        username = req.POST['username']
        phone = req.POST['phone']
        address = req.POST['address']
        
        # Create the user
        user = User.objects.create_user(username=username)
        user.set_password('defaultpassword')  
        user.save()
        
        # Create client profile
        client = Client.objects.create(
            user=user,
            phone=phone,
            address=address
        )
        client.save()
        messages.success(req, 'Client added successfully!')
        return redirect(admdash)
    return render(req, 'agent/add_client.html')

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

def add_evidence(request, case_id):
    case = Case.objects.get(id=case_id)
    
    if request.method == 'POST':
        file = request.FILES['file']
        description = request.POST['description']
        
        evidence = Evidence.objects.create(
            case=case,
            file=file,
            description=description
        )
        evidence.save()
        messages.success(request, 'Evidence added successfully!')
        return redirect('case_details', case_id=case.id)
    
    return render(request, 'agent/add_evidence.html', {
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
        description = req.POST.get('details')
        agent_id = req.POST.get('agent')
        user_id = req.POST.get('user')
        evidence_file = req.FILES.get('evidence')
        evidence_description = req.POST.get('evidence_description')

        if not req.user.is_authenticated:
            messages.error(req, "You need to log in to submit a case.")
            return redirect('log')

        if description and agent_id and evidence_file and evidence_description:
            try:
                agent = get_object_or_404(Agent, id=agent_id)
                user = get_object_or_404(User, id=user_id)
                case = Case.objects.create(
                    assigned_agent=agent.user,
                    category=category,
                    description=description,
                    title=f"Case in {category.c_name}",
                )

                Evidence.objects.create(
                    case=case,
                    file=evidence_file,
                    description=evidence_description,
                )

                # Send email asynchronously in production
                send_mail(
                    subject=f"New Case Assigned: {case.title}",
                    message=f"A new case has been assigned to you.\n\n"
                            f"Category: {category.c_name}\n"
                            f"Title: {case.title}\n"
                            f"Description: {case.description}\n"
                            f"Please log in for more details.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[agent.user.email],
                )

                messages.success(req, "Case submitted successfully.")
                return redirect('user_home')

            except Exception as e:
                messages.error(req, "An error occurred while submitting the case.")
        else:
            messages.error(req, "All fields are required.")
    return render(req, 'client/submitcase.html', {'category': category, 'agents': agents})
    
def chat_view(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    # Ensure that the user is either the client or the assigned agent for this case
    if request.user != case.client and request.user != case.assigned_agent:
        return redirect('home')  # Or show an error page
    
    messages = ChatMessage.objects.filter(case=case).order_by('timestamp')

    if request.method == 'POST':
        message_content = request.POST['message']
        if message_content:
            chat_message = ChatMessage.objects.create(
                case=case,
                sender=request.user,
                message=message_content
            )
            chat_message.save()

    return render(request, 'chat.html', {
        'case': case,
        'messages': messages
    })

def send_message(req, case_id):
    if req.method == 'POST':
        case = get_object_or_404(Case, id=case_id)
        data = json.loads(req.body)
        message_content = data.get('message')
        sender = req.user
        if message_content:
            message = ChatMessage.objects.create(case=case, sender=sender, message=message_content)
            return JsonResponse({'status': 'success', 'message': message.message, 'sender': sender.username})
    return JsonResponse({'status': 'error'}, status=400)

def agent_profile(req, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    cases = Case.objects.filter(assigned_agent=agent.user) 
    return render(req, 'agent/agent_profile.html', {'agent': agent,'cases': cases,})

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
    if req.user != case.assigned_agent.user:
        messages.error(req, "You do not have permission to view this case.")
        return redirect('user_home')

    return render(req, 'agent/case_details.html', {
        'case': case
    })