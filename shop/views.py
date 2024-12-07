import requests
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .inherit import cartData
from .utility import CONSUMER_KEY, CONSUMER_SECRET, BASE_URL, SHORTCODE, PASSKEY
from datetime import datetime
import base64
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm


def index(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    return render(request, "shop/index.html", {'products': products, 'cartItems': cartItems})


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': product.image,
                },
                'quantity': cart[i]["quantity"],
                'get_total': total
            }
            items.append(item)
        except:
            pass
    return render(request, "shop/cart.html", {'items': items, 'order': order, 'cartItems': cartItems})


def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    total = order.get_cart_total

    if request.method == "POST":
        # Retrieve required fields from POST data
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        payment = request.POST.get('payment')

        # Save the checkout details
        checkout_detail = CheckoutDetail.objects.create(
            address=address,
            phone_number=phone_number,
            customer=request.user.customer,
            total_amount=total,
            order=order,
            payment=payment
        )
        checkout_detail.save()

        # Mark order as incomplete for MPESA payments
        if payment == "MPESA":
            # Redirect to MPESA payment page with order ID
            return redirect('mpesa_payment', order_id=order.id)
        else:
            # Mark the order as complete for other payment methods
            order.complete = True
            order.save()
            alert = True
            return render(request, "shop/checkout.html", {'alert': alert, 'id': order.id})

    return render(request, "shop/checkout.html", {'cartItems': cartItems, 'order': order, 'items': items})


def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    print('Action:', action)
    print('productID:', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    update_order.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


@login_required
def product_view(request, myid):
    # Fetch the product and associated data
    product = get_object_or_404(Product, id=myid)
    feature = Feature.objects.filter(product=product)
    reviews = Review.objects.filter(product=product)

    # Cart data
    data = cartData(request)
    cartItems = data['cartItems']

    # Handle POST request for reviews
    if request.method == "POST":
        content = request.POST.get('content', "").strip()
        if not content:
            return render(request, "shop/product_view.html", {
                'product': product,
                'cartItems': cartItems,
                'feature': feature,
                'reviews': reviews,
                'error': "Review content cannot be empty.",
            })

        try:
            # Fetch the logged-in customer's object
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return render(request, "shop/product_view.html", {
                'product': product,
                'cartItems': cartItems,
                'feature': feature,
                'reviews': reviews,
                'error': "Customer profile not found. Please contact support.",
            })

        # Save the review
        review = Review(customer=customer, content=content, product=product)
        review.save()
        return redirect(f"/product_view/{product.id}")

    # Render the product view template
    return render(request, "shop/product_view.html", {
        'product': product,
        'cartItems': cartItems,
        'feature': feature,
        'reviews': reviews,
    })

def search(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        search = request.POST['search']
        products = Product.objects.filter(name__contains=search)
        return render(request, "shop/search.html", {'search': search, 'products': products, 'cartItems': cartItems})
    else:
        return render(request, "shop/search.html")


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "shop/change_password.html", {'alert': alert})
            else:
                currpasswrong = True
                return render(request, "shop/change_password.html", {'currpasswrong': currpasswrong})
        except:
            pass
    return render(request, "shop/change_password.html", {'cartItems': cartItems})


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'shop/contact.html', {'alert': alert})
    return render(request, "shop/contact.html")


def loggedin_contact(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        name = request.user
        email = request.user.email
        phone = request.user.customer.phone_number
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'shop/loggedin_contact.html', {'alert': alert})
    return render(request, "shop/loggedin_contact.html", {'cartItems': cartItems})


def tracker(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        order_id = request.POST['order_id']
        order = Order.objects.filter(id=order_id).first()
        order_items = OrderItem.objects.filter(order=order)
        update_order = UpdateOrder.objects.filter(order_id=order_id)
        print(update_order)
        return render(request, "shop/tracker.html", {'order_items': order_items, 'update_order': update_order})
    return render(request, "shop/tracker.html", {'cartItems': cartItems})


def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST.get('username', '')
            full_name = request.POST.get('full_name', '')
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            phone_number = request.POST.get('phone_number', '')
            email = request.POST.get('email', '')

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                error_message = "Username already exists. Please choose another one."
                return render(request, "shop/register.html", {'error_message': error_message})

            # Check if passwords match
            if password1 != password2:
                alert = True
                return render(request, "shop/register.html", {'alert': alert})

            # Create the user and customer
            user = User.objects.create_user(username=username, password=password1, email=email)
            customers = Customer.objects.create(user=user, name=full_name, phone_number=phone_number, email=email)
            user.save()
            customers.save()

            return redirect("login")

        return render(request, "shop/register.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                alert = True
                return render(request, "shop/login.html", {"alert": alert})
    return render(request, "shop/login.html")


def Logout(request):
    logout(request)
    alert = True
    return render(request, "shop/index.html", {'alert': alert})


def generate_access_token():
    auth_url = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get('access_token')


def mpesa_payment(request, order_id):
    # Retrieve the order using the provided order_id
    order = Order.objects.get(id=order_id)
    total_amount = order.get_cart_total  # Retrieve the total cart amount

    # Pass the total amount to the template
    return render(request, 'shop/mpindex.html', {
        'order': order,
        'total_amount': total_amount
    })


@csrf_exempt
def stk_push(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Create transaction
        transaction = Transaction.objects.create(
            phone_number=phone,
            amount=amount,
            status="Pending",
            description="Awaiting status result",
        )

        # Generate the STK Push payload
        access_token = generate_access_token()
        stk_url = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()).decode()

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://lucent-moxie-7b30b4.netlify.app/",
            "AccountReference": f"Transaction_{transaction.id}",
            "TransactionDesc": "Payment for Services"
        }

        # Send STK Push request
        response = requests.post(stk_url, json=payload, headers=headers)
        response_data = response.json()

        # Update transaction details
        transaction_id = response_data.get('CheckoutRequestID', None)
        transaction.transaction_id = transaction_id
        transaction.description = response_data.get('ResponseDescription', "No Description")
        transaction.save()

        # Create or update the order
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            order.transaction = transaction  # Link the transaction to the order
            order.total = amount  # Assign the paid amount as the order total
            order.complete = True  # Mark the order as complete
            order.save()

            # Redirect to the payment success page with the transaction ID
            return redirect('waiting_page', transaction_id=transaction.id)

    return JsonResponse({'error': "invalid request"}, status=400)

def waiting_page(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, 'shop/waiting.html', {'transaction': transaction})



def customer_support(request):
    return render(request, 'shop/customersupport.html', {'year': datetime.now().year})

def submit_support_ticket(request):
    if request.method == 'POST':
        # Process form data here
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        # Save to database or send an email
        return HttpResponse("Thank you for contacting support. We'll get back to you shortly.")
    return HttpResponse("Invalid request method.")


def faq_page(request):
    return render(request, 'shop/faq.html')



def return_policy(request):
    return render(request, 'shop/return_policy.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect to avoid resubmission issues
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'shop/profile.html', {'form': form})
