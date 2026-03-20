from django.shortcuts import render,redirect,get_object_or_404
from.models import *
from django.contrib import messages
from django.core.mail import send_mail
from datetime import date as date, datetime as dt
from django.db.models import Q, Min, Max
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    return render(request,"index.html")

def contact(request):
    return render(request,"user/contact.html")

def userhome(request):
    return render(request,"user/userhome.html")

def collecthome(request):
    return render(request,"collector/index2.html")

def orghome(request):
    uid=request.session['uid']
    return render(request,"organization/trashhome.html")

def adminhome(request):
    return render(request,"admin/adminhome.html")

def userreg(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        address = request.POST.get("address")
        password = request.POST.get("password")

        if UserReg.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            # return render(request, "user/register.html") 
        else:
            user = Login.objects.create(email=email, password=password, userType='user')
            UserReg.objects.create(user=user, firstname=firstname, lastname=lastname, email=email,
                                   address=address, password=password)
            messages.info(request, "Registration successful")
            return redirect("/login/") 

    return render(request, "userregister.html")



def organizerreg(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if UserReg.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            return render(request, "organizerregister.html") 
        else:
            user = Login.objects.create(email=email, password=password, userType='organizer')
            Organizer.objects.create(user=user, firstname=firstname, lastname=lastname, email=email, password=password)
            messages.info(request, "Registration successful")
            return redirect("/login/") 

    return render(request, "organizerregister.html")

def collectorreg(request):
    organizers = Organizer.objects.filter(status='approved')
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        idproof = request.FILES.get('idproof')
        organizer_id = request.POST.get("organizer_id")

        if Login.objects.filter(email=email).exists():
            messages.info(request, "Email already exists")
            return render(request, "coll_reg.html", {'organizers': organizers}) 
        else:
            user = Login.objects.create(email=email, password=password, userType='Collector')
            org = None
            if organizer_id:
                org = Organizer.objects.get(id=organizer_id)
            Collector.objects.create(
                user=user, 
                organizer=org, 
                firstname=firstname, 
                lastname=lastname, 
                email=email,
                idproof=idproof, 
                password=password
            )
            messages.info(request, "Registration successful")
            return redirect("/login/") 

    return render(request, "coll_reg.html", {'organizers': organizers})


def login(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Login.objects.filter(email=email).first()
        if user:
            if user.password == password:
                if user.userType == "Admin":
                    request.session['admin_id'] = user.id # Set admin session
                    return redirect('/adminhome/')

                elif user.userType == "organizer":
                    organizer = Organizer.objects.filter(user=user).first()
                    if organizer:
                        if organizer.status == "approved":
                            request.session['uid'] = organizer.user_id
                            messages.success(request, "Login Successful as Organizer")
                            return redirect('/orghome/')
                        else:
                            messages.info(request, "Your account is pending approval")
                    else:
                        messages.error(request, "Organizer profile not found.")
                    return redirect('/login/')
                
                elif user.userType == "Collector":
                    coll = Collector.objects.filter(user=user).first()
                    if coll:
                        if coll.status == "approved":
                            request.session['uid'] = coll.user_id
                            messages.success(request, "Login Successful")
                            return redirect('/collecthome/')
                        else:
                            messages.info(request, "Your account is pending approval")
                    else:
                        messages.error(request, "Organizer profile not found.")
                    return redirect('/login/')

                elif user.userType == "user":
                    user_profile = UserReg.objects.filter(user=user).first()
                    if user_profile:
                        request.session['uid'] = user_profile.id
                        messages.success(request, "Login Successful as User")
                        return redirect('/userhome/')
                    else:
                        messages.error(request, "User profile not found.")
                    return redirect('/login/')
                
                else:
                    messages.error(request, "Invalid user type.")
                    return redirect('/login/')
            else:
                messages.error(request, "Incorrect password.")
                return redirect('/login/')
        else:
            messages.error(request, "Email not found.")
            return redirect('/login/')

    return render(request, 'login.html')

def vieworg(request):
    if 'admin_id' not in request.session:
        return redirect('/login/')
    orgz = Organizer.objects.all()
    return render(request,"admin/organizerview.html",{'orgz':orgz})

def uservieworg(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    orgz = Organizer.objects.filter(status='approved')
    return render(request,"user/view_organizers.html",{'orgz':orgz})

def accept(request):
    if 'admin_id' not in request.session:
        return redirect('/login/')
    id = request.GET.get("id")
    user = Organizer.objects.filter(id=id).first()
    if user:
        if user.status != "pending":
            messages.warning(request, f"Organizer {id} is already {user.status}.")
            return redirect('/vieworg/')
        user.status = "approved"
        user.save() 
        messages.info(request,'Approved successfully')
    return redirect('/vieworg/')

def reject(request):
    id = request.GET.get("id")
    user = Organizer.objects.filter(id=id).first()
    if user:
        if user.status != "pending":
            messages.warning(request, f"Organizer {id} is already {user.status}.")
            return redirect('/vieworg/')
        user.status = "rejected" 
        user.save() 
    messages.info(request,'User will Rejected Success')
    return redirect('/vieworg/')


def submitrequest(request):
    uid = request.session["uid"]
    user = UserReg.objects.get(id=uid)
    
    # Pre-select organizer if passed via GET
    selected_org_id = request.GET.get('org_id')
    
    if not selected_org_id:
        messages.info(request, "Please select an organizer first.")
        return redirect('/uservieworg/')

    org = get_object_or_404(Organizer, id=selected_org_id)

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        house_number = request.POST.get("house_number")
        location = request.POST.get("location")
        phone_number = request.POST.get("phone_number")
        waste_type = request.POST.get("waste_type")
        description = request.POST.get("description")

        WasteCollectionRequest.objects.create(
            user=user,
            name=name,
            address=address,
            house_number=house_number,
            location=location,
            phone_number=phone_number,
            waste_type=waste_type,
            description=description,
            organizer=org
        )

        messages.success(request, "Request submitted successfully.")
        return redirect('/userrequestdetails/')

    return render(request, "user/weastrequest.html", {
        'org': org,
        'user': user,
    })

def edit_request(request, request_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    waste_request = get_object_or_404(WasteCollectionRequest, id=request_id, user_id=uid)
    
    # Only allow editing if request is still Pending
    if waste_request.status.lower() != 'pending':
        messages.warning(request, "You can only edit requests that are still pending.")
        return redirect('/userrequestdetails/')

    if request.method == "POST":
        waste_request.name = request.POST.get("name")
        waste_request.address = request.POST.get("address")
        waste_request.house_number = request.POST.get("house_number")
        waste_request.location = request.POST.get("location")
        waste_request.phone_number = request.POST.get("phone_number")
        waste_request.waste_type = request.POST.get("waste_type")
        waste_request.description = request.POST.get("description")
        waste_request.save()
        
        messages.success(request, "Request updated successfully.")
        return redirect('/userrequestdetails/')

    return render(request, "user/edit_request.html", {"waste_request": waste_request})

def ad(request):
    Login.objects.create(email="admin@gmail.com",password="admin@123",userType="Admin")
    return redirect("/")

def requestdetails(request): 
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    # Get the organizer profile for the logged-in user
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    if not organizer:
        messages.error(request, "Organizer profile not found.")
        return redirect('/login/')

    # Fetch requests specifically assigned to this organizer
    reqs = WasteCollectionRequest.objects.filter(organizer=organizer)

    # Status counts for summary cards
    pending_count = reqs.filter(status__iexact='Pending').count()
    assigned_count = reqs.filter(status__iexact='Assigned').count()
    picked_count = reqs.filter(status__iexact='Picked Up').count()
    rejected_count = reqs.filter(status__iexact='rejected').count()

    # Fetch approved collectors registered under this organizer
    collectors = Collector.objects.filter(status='approved', organizer=organizer)

    return render(request, "organization/requestdetails.html", {
        'req': reqs,
        'collectors': collectors,
        'pending_count': pending_count,
        'assigned_count': assigned_count,
        'picked_count': picked_count,
        'rejected_count': rejected_count,
    })


def assign_collector(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        collector_id = request.POST.get("collector_id")
        uid = request.session.get('uid')
        
        if not uid:
            messages.error(request, "Session expired. Please login again.")
            return redirect('/login/')

        waste_request = get_object_or_404(WasteCollectionRequest, id=request_id)
        
        # Security check: Ensure logged in user is the organizer profile
        login_user = Login.objects.filter(id=uid).first()
        organizer = Organizer.objects.filter(user=login_user).first()

        if not organizer:
            messages.error(request, "Organizer profile not found.")
            return redirect('/login/')

        # Verify collector belongs to this organizer
        collector = get_object_or_404(Collector, id=collector_id, organizer=organizer)

        if waste_request.organizer and waste_request.organizer != organizer:
            messages.error(request, "You are not authorized to assign this request.")
            return redirect('/requestdetails/')

        waste_request.collector = collector
        waste_request.assign_status = "Assigned"
        
        # Consistent status handling: Move to Assigned so collector can manage it
        waste_request.status = 'Assigned'
        
        # Ensure the organizer is assigned if it was unassigned
        if not waste_request.organizer:
            waste_request.organizer = organizer
            
        waste_request.save()
        messages.success(request, f"Successfully assigned {collector.firstname} to Request #{request_id}")

    return redirect('/requestdetails/')

def pay_collector(request):
    id = request.GET.get("id") or request.POST.get("request_id")
    uid = request.session.get('uid')

    if not uid:
        return redirect('/login/')

    waste_request = get_object_or_404(WasteCollectionRequest, id=id)

    # Security: only assigned organizer can pay
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()

    if not organizer or waste_request.organizer != organizer:
        messages.error(request, "You are not authorized to make this payment.")
        return redirect('/requestdetails/')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            waste_request.amount = amount
            waste_request.collector_payment_status = 'Paid'
            waste_request.status = 'Paid'
            waste_request.save()
            messages.success(request, f"Payment of ₹{amount} made to collector for Request #{id}.")
            return redirect('/requestdetails/')
        else:
            messages.error(request, "Please enter a valid amount.")

    return render(request, 'organization/pay_collector.html', {'waste_request': waste_request})


def acceptwaste(request):
    if request.method == 'POST':
        id = request.POST.get("id")
        amount = request.POST.get("amount")
    else:
        id = request.GET.get("id")
        
    uid = request.session.get('uid')
    
    # Security check: Ensure logged in user is the assigned organizer
    waste_request = WasteCollectionRequest.objects.filter(id=id).first()
    if not waste_request:
        messages.error(request, "Request not found.")
        return redirect('/requestdetails/')
        
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    if waste_request.organizer and waste_request.organizer != organizer:
        messages.error(request, "You are not authorized to approve this request.")
        return redirect('/requestdetails/')

    if waste_request.status == "approved" and waste_request.payment_status == "Paid":
        messages.warning(request, "This request is already paid and cannot be modified.")
        return redirect('/requestdetails/')
        
    waste_request.status = "approved"
    
    # Set the amount if provided via POST
    if request.method == 'POST' and amount:
        try:
            waste_request.amount = float(amount)
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect('/requestdetails/')
            
    if not waste_request.organizer:
        waste_request.organizer = organizer
        
    waste_request.save() 
    messages.info(request, f'Request Approved. Amount set to ₹{waste_request.amount}')
    return redirect('/requestdetails/')

def approvepaper(request):
    if 'uid' not in request.session:
        messages.error(request, "You must be logged in to approve requests.")
        return redirect('/login/') 

    id = request.GET.get("id")
    if not id:
        messages.error(request, "Invalid request ID.")
        return redirect("/coll_requestdetails/")

    user_id = request.session.get("uid")
    user = Login.objects.get(id=user_id)  # Fetch user from session

    collector = get_object_or_404(Collector, user=user)  # Get collector by user

    user_request = get_object_or_404(WasteCollectionRequest, id=id)
    if user_request.status != "Pending":
        messages.warning(request, f"Request {id} is already {user_request.status}.")
        return redirect("/coll_requestdetails/")
        
    user_request.status = "approved"
    user_request.collector = collector  # Assign the logged-in collector
    user_request.save()

    messages.success(request, f"Request {id} approved and assigned to {collector.firstname}.")
    return redirect("/coll_requestdetails/")


def rejectwaste(request):
    id = request.GET.get("id")
    uid = request.session.get('uid')
    
    waste_request = WasteCollectionRequest.objects.filter(id=id).first()
    if not waste_request:
        messages.error(request, "Request not found.")
        return redirect('/requestdetails/')
        
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    if waste_request.organizer and waste_request.organizer != organizer:
        messages.error(request, "You are not authorized to reject this request.")
        return redirect('/requestdetails/')

    waste_request.status = "rejected" 
    waste_request.save() 
    messages.info(request,'Request rejected')
    return redirect('/requestdetails/')

def mark_reached(request):
    """Collector marks they have reached the pickup location."""
    id = request.GET.get("id")
    uid = request.session.get('uid')

    collection_request = WasteCollectionRequest.objects.filter(id=id).first()
    if not collection_request:
        messages.error(request, 'Request not found.')
        return redirect('/coll_requestdetails/')

    login_user = Login.objects.filter(id=uid).first()
    collector = Collector.objects.filter(user=login_user).first()

    if not collector or collection_request.collector != collector:
        messages.error(request, "You are not authorized to update this request.")
        return redirect('/coll_requestdetails/')

    collection_request.status = "Reached"
    collection_request.save()
    messages.info(request, 'Status updated: You have reached the pickup location.')
    return redirect('/coll_requestdetails/')


def wepicked(request):
    """Collector marks they have picked up the waste."""
    id = request.GET.get("id")
    uid = request.session.get('uid')

    collection_request = WasteCollectionRequest.objects.filter(id=id).first()
    if not collection_request:
        messages.error(request, 'Request not found.')
        return redirect('/coll_requestdetails/')

    login_user = Login.objects.filter(id=uid).first()
    collector = Collector.objects.filter(user=login_user).first()

    if not collector or collection_request.collector != collector:
        messages.error(request, "You are not authorized to update this request.")
        return redirect('/coll_requestdetails/')

    collection_request.status = "Picked Up"
    collection_request.save()
    messages.success(request, 'Waste picked up successfully! Organiser will process payment.')
    return redirect('/coll_requestdetails/')


def user_view(request):
    users = UserReg.objects.all()
    return render(request, 'admin/userview.html', {'users': users})


def collector_view(request):
    collectors = Collector.objects.all().select_related('organizer')
    return render(request, 'admin/collectorview.html', {'collectors': collectors})

def accept_collector(request, id):
    collector = Collector.objects.filter(id=id).first()
    if collector:
        if collector.status != "pending":
            messages.warning(request, f"Collector {id} is already {collector.status}.")
            return redirect('collector_view')
        collector.status = "approved"
        collector.save()
        messages.success(request, 'User approved successfully')
    return redirect('collector_view')

def reject_collector(request, id):
    collector = Collector.objects.filter(id=id).first()
    if collector:
        if collector.status != "pending":
            messages.warning(request, f"Collector {id} is already {collector.status}.")
            return redirect('collector_view')
        collector.status = "rejected"
        collector.save()
        messages.error(request, 'User rejected successfully')
    return redirect('collector_view')


def userrequestdetails(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    reqe = WasteCollectionRequest.objects.filter(user_id=uid).order_by('-request_date')
    return render(request, "user/requestdetails.html", {'req': reqe})

def userpay(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
        
    if request.method == 'POST':
        request_id = request.POST.get('id')
        waste_request = get_object_or_404(WasteCollectionRequest, id=request_id, user_id=uid)
        
        # Process payment (mock)
        waste_request.payment_status = 'Paid'
        waste_request.save()
        messages.success(request, f"Payment of ₹{waste_request.amount} was successful.")
        return redirect('/userrequestdetails/')
        
    else:
        request_id = request.GET.get("id")
        waste_request = get_object_or_404(WasteCollectionRequest, id=request_id, user_id=uid)
        
        if waste_request.payment_status == 'Paid':
            messages.info(request, "This request has already been paid.")
            return redirect('/userrequestdetails/')
            
        return render(request, 'user/user_pay.html', {'waste_request': waste_request})


def addproduct(request):
    uid = request.session["uid"]
    print(uid)
    org = Organizer.objects.get(user_id=uid)  
    if request.method == 'POST':
        product_name = request.POST['product_name']
        description = request.POST.get('product_description', '')
        price = request.POST['price']
        image = request.FILES.get('image')
        
        org = Organizer.objects.filter(user_id=uid).first()
        print(org,',##############')
        b= RecycledProduct.objects.create(
            org=org,
            product_name=product_name,
            description=description,
            price=price,
            image=image
        )
        return redirect('/productlist/')
    return render(request,"organization/addproduct.html")


def editproduct(request):
    id = request.GET.get('id')
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    product = get_object_or_404(RecycledProduct, id=id)
    
    # Ownership Check
    if product.org.user_id != uid:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect('/productlist/')

    if request.method == 'POST':
        product.product_name = request.POST['product_name']
        product.description = request.POST.get('product_description', '')
        product.price = request.POST['price']
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully')
        return redirect('/productlist/')
    return render(request, "organization/editproduct.html", {'product': product})


def productlist(request):
    uid = request.session["uid"]
    pro = RecycledProduct.objects.filter(org__user_id=uid)  
    return render(request,"organization/productlist.html",{'pro':pro})

def userproductlist(request):
    uid = request.session["uid"]
    proo = RecycledProduct.objects.all()
    return render(request,"user/product.html",{'proo':proo})

def deleteimg(request):
    id = request.GET.get('id')
    uid = request.session['uid']
    # Filter by id and org__user_id to ensure only the owner can delete
    deleted_count, _ = RecycledProduct.objects.filter(id=id, org__user_id=uid).delete()
    if deleted_count > 0:
        messages.info(request, "Successfully removed")
    else:
        messages.error(request, "You are not authorized to delete this product or it does not exist.")
    return redirect('/productlist/')



def buy(request):
    uid = request.session.get('uid')
    if not uid:
        messages.error(request, "User not logged in.")
        return redirect('/login/')

    user = UserReg.objects.filter(id=uid).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect('/login/')

    product_id = request.GET.get("id")
    product = get_object_or_404(RecycledProduct, id=product_id)
    
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        order = Order.objects.create(
            product=product,
            user=user,  # Ensure this is not None
            name=name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )
        return redirect(f'/payment/?order_id={order.id}')  

    return render(request, 'user/createorder.html', {'product': product})



def update_pickup_date(request, request_id):
    uid = request.session.get('uid')
    if request.method == "POST":
        pickup_date = request.POST.get("pickup_date")
        collector_id = request.POST.get("collector_id")

        waste_request = get_object_or_404(WasteCollectionRequest, id=request_id)
        
        # Security check: Only the assigned collector can update this
        login_user = Login.objects.filter(id=uid).first()
        collector = Collector.objects.filter(user=login_user).first()
        
        if waste_request.collector != collector:
            messages.error(request, "You are not authorized to schedule this pickup.")
            return redirect("coll_requestdetails")

        # Backend Validation: Prevent past dates
        if pickup_date < str(date.today()):
            messages.error(request, "Pickup date cannot be in the past.")
            return redirect("coll_requestdetails")

        waste_request.pickup_date = pickup_date
        waste_request.status = "Dated"

        # Assign the collector if provided (usually redundant if already assigned)
        if collector_id:
            assigned_collector = get_object_or_404(Collector, id=collector_id)
            waste_request.collector = assigned_collector 

        waste_request.save()

        # Send notification email to the user
        try:
            send_mail(
                "Waste Pickup Scheduled",
                f"Your waste collection is scheduled for {pickup_date}.",
                settings.EMAIL_HOST_USER, # Use settings
                [waste_request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending mail: {e}")

        messages.success(request, "Pickup date assigned successfully.")
        return redirect("coll_requestdetails")

    return redirect("coll_requestdetails")


def userorderdetails(request):
    uid = request.session['uid'] 
    abc = Order.objects.select_related('product').filter(user_id=uid)
    return render(request,"user/orderdetails.html",{'abc':abc})

def orderdetailsorg(request):
    uid = request.session['uid'] 
    # Only show orders for products belonging to this organizer
    abc = Order.objects.select_related('product').filter(product__org__user_id=uid)
    return render(request,"organization/orderdetails.html",{'abc':abc})

def payment(request):
    uid = request.session['uid']  
    order_id =request.GET.get("order_id")

    print(order_id,"_____________________")
    product = Order.objects.filter(id=order_id)
    
    order = Order.objects.select_related('product').filter(id=order_id).first()    
    if request.method == 'POST':
        order.payment_status = 'paid'
        order.save()
        messages.success(request, 'Payment successful')
        # Redirect to user order history instead of productreview
        return redirect('/userorderdetails/')
    return render(request, "user/payment.html", {'order': order})


def shipped(request):
    id = request.GET.get("id")
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
        
    order = Order.objects.select_related('product__org').filter(id=id).first()
    if order:
        # Ownership Check
        if order.product.org.user_id != uid:
            messages.error(request, "You are not authorized to ship this order.")
            return redirect('/orderdetailsorg/')
            
        if order.status != "Pending":
            messages.warning(request, f"Order {id} is already {order.status}.")
            return redirect('/orderdetailsorg/')
            
        # Security check: Ensure order is paid before shipping
        if order.payment_status.lower() != 'paid':
            messages.error(request, "Cannot ship unpaid orders. Awaiting user payment.")
            return redirect('/orderdetailsorg/')
            
        order.status = "Shipped"
        order.save() 
        messages.info(request, 'Shipped successfully')
    return redirect('/orderdetailsorg/')

def delivered(request):
    id = request.GET.get("id")
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
        
    order = Order.objects.select_related('product__org').filter(id=id).first()
    if order:
        # Ownership Check
        if order.product.org.user_id != uid:
            messages.error(request, "You are not authorized to deliver this order.")
            return redirect('/orderdetailsorg/')
            
        if order.status != "Shipped":
            messages.warning(request, f"Order {id} is {order.status}. Must be Shipped first.")
            return redirect('/orderdetailsorg/')
        order.status = "delivered"
        order.save() 
        messages.info(request,'delivered successfully')
    return redirect('/orderdetailsorg/')


def add_request_feedback(request, request_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    waste_request = get_object_or_404(WasteCollectionRequest, id=request_id, user_id=uid)
    
    # Restrict feedback to Completed (Picked Up) requests only
    if waste_request.status.lower() != 'picked up':
        messages.error(request, "Feedback can only be provided after the request has been picked up.")
        return redirect('/userrequestdetails/')

    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')
        if feedback_text:
            if RequestFeedback.objects.filter(request=waste_request).exists():
                messages.warning(request, "You have already provided feedback for this request.")
                return redirect('/userrequestdetails/')
            
            user = UserReg.objects.get(id=uid)
            RequestFeedback.objects.create(
                request=waste_request,
                user=user,
                feedback_text=feedback_text
            )
            messages.success(request, "Feedback added successfully.")
            return redirect('/userrequestdetails/')
        else:
            messages.error(request, "Feedback text cannot be empty.")
            
    return render(request, 'user/add_feedback.html', {'waste_request': waste_request})

def edit_request_feedback(request, feedback_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedback = get_object_or_404(RequestFeedback, id=feedback_id, user_id=uid)
    
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')
        if feedback_text:
            feedback.feedback_text = feedback_text
            feedback.save()
            messages.success(request, "Feedback updated successfully.")
            return redirect('/userrequestdetails/')
        else:
            messages.error(request, "Feedback text cannot be empty.")
            
    return render(request, 'user/add_feedback.html', {'feedback': feedback, 'waste_request': feedback.request})

def delete_request_feedback(request, feedback_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedback = get_object_or_404(RequestFeedback, id=feedback_id, user_id=uid)
    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect('/userrequestdetails/')

def user_view_feedback(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedbacks = RequestFeedback.objects.filter(user_id=uid).select_related('request').order_by('-created_date')
    return render(request, 'user/view_feedback.html', {'feedbacks': feedbacks})

def user_view_order_feedback(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedbacks = OrderFeedback.objects.filter(user_id=uid).select_related('order__product').order_by('-created_date')
    return render(request, 'user/view_order_feedback.html', {'feedbacks': feedbacks})

def reviewslist(request):
    id = request.GET.get("id")  
    uid = request.session.get('uid') 
    reviews = ProductReview.objects.filter(id = id)
    return render(request, 'user/rating.html', {'reviews': reviews})

def productreview(request):
    # product_id = request.GET.get("id")
    uid = request.session.get('uid')
    user = UserReg.objects.get(id=uid)
    product = RecycledProduct.objects.filter().first()
   
    if request.POST:
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        proriv=ProductReview.objects.create(user=user,product=product,rating=rating,review_text=review_text)
        proriv.save()
        messages.info(request,"sucessfully add the review")
        return redirect('/userorderdetails/')
    
    return render(request,"user/rating.html", {'product': product})

def orgreviewlist(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    # Get the organizer profile
    organizer = get_object_or_404(Organizer, user_id=uid)
    
    # Get products belonging to this organizer
    products = RecycledProduct.objects.filter(org=organizer)
    
    # Get classic product reviews for these products
    classic_reviews = ProductReview.objects.filter(product__in=products).order_by('-review_date')
    
    # Get order-specific feedbacks for these products
    order_feedbacks = OrderFeedback.objects.filter(order__product__in=products).order_by('-created_date')
    
    # Get collection feedbacks for this organizer
    collection_feedbacks = RequestFeedback.objects.filter(request__organizer=organizer).order_by('-created_date')
    
    return render(request, "organization/reviewlist.html", {
        'classic_reviews': classic_reviews,
        'order_feedbacks': order_feedbacks,
        'collection_feedbacks': collection_feedbacks,
        'products': products
    })


def adminorderlist(request):
    fuu = Order.objects.all()
    return render(request,'admin/orderlist.html',{'fuu':fuu})

def adminfeedbacklist(request):
    request_feedback = RequestFeedback.objects.all().select_related('request', 'user').order_by('-created_date')
    order_feedback = OrderFeedback.objects.all().select_related('order', 'user').order_by('-created_date')
    
    return render(request, 'admin/feedbackview.html', {
        'request_feedback': request_feedback,
        'order_feedback': order_feedback
    })


def adminproductlist(request):
    pr = RecycledProduct.objects.all()
    return render(request,"admin/adminviewproduct.html",{'pr':pr})

# 
def coll_requestdetails(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')

    login_user = Login.objects.filter(id=uid).first()
    collector = Collector.objects.filter(user=login_user).first()

    if not collector:
        messages.error(request, "Collector profile not found.")
        return redirect('/login/')

    # Only show requests assigned to this collector
    req = WasteCollectionRequest.objects.filter(collector=collector)
    today = date.today()
    return render(request, "collector/requestdetails.html", {
        'req': req,
        'today': today
    })

def coll_accept(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    if not organizer:
        messages.error(request, "Organizer profile not found.")
        return redirect('/login/')
        
    req = Collector.objects.filter(organizer=organizer)
    return render(request,"organization/requestdetails_col.html",{'req':req})

def acceptwaste_col(request):
    id = request.GET.get("id")
    uid = request.session.get('uid')
    
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    user = Collector.objects.filter(id=id).first()
    if user:
        if user.organizer != organizer:
            messages.error(request, "You are not authorized to approve this collector.")
            return redirect('/coll_accept/')
            
        if user.status != "pending":
            messages.warning(request, f"Collector {id} is already {user.status}.")
            return redirect('/coll_accept/')
        user.status = "approved"
        user.save() 
        messages.info(request,'Approved successfully')
    return redirect('/coll_accept/')

def rejectwaste_col(request):
    id = request.GET.get("id")
    uid = request.session.get('uid')
    
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    user = Collector.objects.filter(id=id).first()
    if user:
        if user.organizer != organizer:
            messages.error(request, "You are not authorized to reject this collector.")
            return redirect('/coll_accept/')
            
        if user.status != "pending":
            messages.warning(request, f"Collector {id} is already {user.status}.")
            return redirect('/coll_accept/')
        user.status = "rejected" 
        user.save() 
        messages.info(request,'User will Rejected Success')
    return redirect('/coll_accept/')

def rejectwaste_adq(request):
    id = request.GET.get("id")
    user_request = WasteCollectionRequest.objects.filter(id=id).first()

    if user_request:
        user_request.status = "rejected"
        user_request.collector = None  # Remove assigned collector
        user_request.save()
        messages.info(request, "Collector has been rejected successfully.")

    return redirect("/coll_requestdetails/")


def delete(request):
    id=request.GET.get('id')
    delete=ProductReview.objects.filter(id=id).delete()
    messages.info(request,"Deteted")
    return redirect('/orgreviewlist')

def admin_delete_request_feedback(request, id):
    RequestFeedback.objects.filter(id=id).delete()
    messages.success(request, "Request feedback removed successfully.")
    return redirect('/adminfeedbacklist/')

def admin_delete_order_feedback(request, id):
    OrderFeedback.objects.filter(id=id).delete()
    messages.success(request, "Order feedback removed successfully.")
    return redirect('/adminfeedbacklist/')


def paper_collection_requests(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    login_user = Login.objects.filter(id=uid).first()
    collector = Collector.objects.filter(user=login_user).first()
    
    if not collector:
        messages.error(request, "Collector profile not found.")
        return redirect('/login/')
        
    # Only show requests assigned to this collector
    req = WasteCollectionRequest.objects.filter(collector=collector)
    organizers = Organizer.objects.filter(status="approved")  
    return render(request, "collector/paper_collection_requests.html", {"req": req, "organizers": organizers})


def assign_to_organizer(request, request_id):
    uid = request.session.get("uid")
    if request.method == "POST":
        organizer_id = request.POST.get("organizer_id")
        waste_request = get_object_or_404(WasteCollectionRequest, id=request_id)
        
        # Security check: Only the assigned collector can assign an organizer
        login_user = Login.objects.filter(id=uid).first()
        collector = Collector.objects.filter(user=login_user).first()
        
        if waste_request.collector != collector:
            messages.error(request, "You are not authorized to assign an organizer to this request.")
            return redirect("/paper_collection_requests/")

        organizer = get_object_or_404(Organizer, id=organizer_id)
        
        waste_request.organizer = organizer
        waste_request.assign_status = "Assigned"
        waste_request.save()
        
        messages.success(request, "Request assigned to organizer successfully.")
        return redirect("/paper_collection_requests/")  
    return redirect("/paper_collection_requests/")


def reply(request, id):
    uid = request.session.get("uid")
    request_obj = get_object_or_404(WasteCollectionRequest, id=id)
    
    # Security check: Only the assigned organizer can reply
    login_user = Login.objects.filter(id=uid).first()
    organizer = Organizer.objects.filter(user=login_user).first()
    
    if request_obj.organizer != organizer:
        messages.error(request, "You are not authorized to reply to this request.")
        return redirect('requestdetails')

    if request.method == "POST":
        request_obj.reply_message = request.POST.get("reply_message")
        request_obj.save()
        messages.success(request, "Reply sent successfully.")
        return redirect('requestdetails')  # Simplified redirect

    return render(request, 'organization/reply.html', {'request_obj': request_obj})




def collector_replies(request):
    
    user_id = request.session.get('uid')
    try:
        login_user = Login.objects.get(id=user_id)
        collector = Collector.objects.get(user=login_user)
    except (Login.DoesNotExist, Collector.DoesNotExist):
        messages.error(request, "Collector profile not found.")
        return redirect('/login/')

    requests = WasteCollectionRequest.objects.filter(
        collector=collector
    ).exclude(reply_message__isnull=True).exclude(reply_message__exact='')

    return render(request, 'collector/collector_replies.html', {'requests': requests})


def add_order_feedback(request, order_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    order = get_object_or_404(Order, id=order_id, user_id=uid)
    
    # Condition: Feedback only for delivered orders
    if order.status.lower() != 'delivered':
        messages.warning(request, "You can only provide feedback for delivered orders.")
        return redirect('/userorderdetails/')

    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')
        if feedback_text:
            if OrderFeedback.objects.filter(order=order).exists():
                messages.warning(request, "You have already provided feedback for this order.")
                return redirect('/userorderdetails/')
            
            user = UserReg.objects.get(id=uid)
            OrderFeedback.objects.create(
                order=order,
                user=user,
                feedback_text=feedback_text
            )
            messages.success(request, "Feedback added successfully.")
            return redirect('/userorderdetails/')
        else:
            messages.error(request, "Feedback text cannot be empty.")
            
    return render(request, 'user/add_order_feedback.html', {'order': order})

def edit_order_feedback(request, feedback_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedback = get_object_or_404(OrderFeedback, id=feedback_id, user_id=uid)
    
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')
        if feedback_text:
            feedback.feedback_text = feedback_text
            feedback.save()
            messages.success(request, "Feedback updated successfully.")
            return redirect('/userorderdetails/')
        else:
            messages.error(request, "Feedback text cannot be empty.")
            
    return render(request, 'user/add_order_feedback.html', {'feedback': feedback, 'order': feedback.order})

def delete_order_feedback(request, feedback_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login/')
    
    feedback = get_object_or_404(OrderFeedback, id=feedback_id, user_id=uid)
    feedback.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect('/userorderdetails/')
