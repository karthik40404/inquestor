from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *

# Create your views here.
def log(req):
    
    if req.user.is_authenticated:
        if req.user.is_superuser:
            return redirect(admdash)
        
        try:
            agent = Agent.objects.get(user=req.user)
            return redirect(agent_dashboard)
        except Agent.DoesNotExist:
            pass
        
        try:
            client = Client.objects.get(user=req.user)
            return redirect(client_dashboard)
        except Client.DoesNotExist:
            pass

        messages.warning(req, "You do not have access to any specific dashboard.")
        return redirect(client_dashboard)
    
    if req.method == "POST":
        email = req.POST['email']
        psw = req.POST['psw']
        
        user = authenticate(username=email, password=psw)
        
        if user is not None:
            if user.is_active:
                login(req, user)
                return redirect(log)  
            else:
                messages.warning(req, "Your account is inactive. Please contact support.")
                return redirect(log)
        else:
            messages.error(req, "Invalid email or password. Please try again.")
            return redirect(log)
        
    return render(req, 'login.html')

def lout(req):
    logout(req)
    return redirect('log')

def admdash(req):
    cases = Case.objects.all()
    agents = Agent.objects.all()
    clients = Client.objects.all()
    categories = CaseCategory.objects.all()
    return render(req, 'admin/admindash.html', {'cases': cases,'agents': agents,'clients': clients,'categories': categories,})

def add_agent(req):
    if req.method == 'POST':
        username = req.POST['username']
        phone = req.POST['phone']
        address = req.POST['address']
        
        # Create the user first
        user = User.objects.create_user(username=username)
        user.set_password('defaultpassword') 
        user.save()
        
        # Create agent profile
        agent = Agent.objects.create(
            user=user,
            phone=phone,
            address=address,
            is_active=True
        )
        agent.save()
        messages.success(req, 'Agent added successfully!')
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

def add_client(req):
    if req.method == 'POST':
        username = req.POST['username']
        phone = req.POST['phone']
        address = req.POST['address']
        
        # Create the user
        user = User.objects.create_user(username=username)
        user.set_password('defaultpassword')  # You can set a default password here
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
    return render(req, 'admin/add_client.html')

def list_clients(req):
    clients = Client.objects.all()
    return render(req, 'admin/list_clients.html', {
        'clients': clients
    })

def agent_dashboard(req):
    cases = Case.objects.filter(assigned_agent=req.user)
    return render(req, 'agent/agent_dashboard.html', {
        'cases': cases
    })

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

