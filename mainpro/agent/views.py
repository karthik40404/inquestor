from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from .models import *
import random,string

# Create your views here.

def landing_page(req):
    if 'admin' in req.session:
        return redirect('admdash')  # Redirect admin
    if 'agent' in req.session:
        return redirect('agent_dashboard')  # Redirect agent
    if 'user' in req.session:
        return redirect('client_dashboard')  # Redirect user
    
    case_categories = CaseCategory.objects.all()
    return render(req, 'landing_page.html',{'case_categories': case_categories})  # Show landing page


def log(req):
    # Redirect based on session roles
    if 'admin' in req.session:
        return redirect(admdash)  # Admin dashboard
    if 'agent' in req.session:
        return redirect(agent_dashboard)  # Agent dashboard
    if 'user' in req.session:
        return redirect(client_dashboard)  # User home

    # Handle POST request for login
    if req.method == 'POST':
        email = req.POST['email']
        psw = req.POST['psw']
        data = authenticate(username=email, password=psw)
        print(data)

        if data:
            login(req, data)

            # Check roles and redirect accordingly
            if data.is_superuser:
                req.session['admin'] = email  # Set admin session
                return redirect(admdash)

            # Check if the user is an agent
            try:
                agent = Agent.objects.get(user=data)  # Assuming Agent model has a `user` ForeignKey
                req.session['agent'] = email  # Set agent session
                return redirect(agent_dashboard)
            except Agent.DoesNotExist:
                pass

            # If neither admin nor agent, assume a regular user
            req.session['user'] = email  # Set user session
            return redirect(client_dashboard)

        else:
            # Authentication failed
            messages.warning(req, "Incorrect username or password.")
            return redirect(log)

    # Render login page for GET request
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
        user = User.objects.create_user(username=username, email=email)
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
        description = req.POST['description']
        
        category = CaseCategory.objects.create(
            c_name=c_name,
            description=description
        )
        category.save()
        messages.success(req, 'Category added successfully!')
        return redirect(admdash)  # Redirect back to the admin dashboard
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
    cases = Case.objects.filter(assigned_agent=req.user)
    
    # Calculate statistics
    total_cases = cases.count()
    open_cases = cases.filter(status='Open').count()
    closed_cases = cases.filter(status='Closed').count()
    
    return render(req, 'agent/agent_dashboard.html', {
        'cases': cases,
        'total_cases': total_cases,
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        'agent': req.user 
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

def client_dashboard(req):
    client = Client.objects.get(user=req.user)
    cases = Case.objects.filter(client=client)
    return render(req, 'client/client_dashboard.html', {'cases': cases})

def cases_by_category(req, category_id):
    category = get_object_or_404(CaseCategory, id=category_id)

    cases = Case.objects.filter(category=category)
    
    return render(req, 'cases_by_category.html', {
        'category': category,
        'cases': cases,
    })