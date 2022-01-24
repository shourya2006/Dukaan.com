from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.views.decorators.csrf import csrf_exempt
# Import for paginating the page
from django.core.paginator import Paginator

def store(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    products = Product.objects.all()
    p = Paginator(Product.objects.all(), 6)
    page = request.GET.get('page')
    prods = p.get_page(page)
    nums = "a" * prods.paginator.num_pages
    context = {"products": products, "cartItems": cartItems , 'prods' : prods , 'nums' : nums}
    return render(request, "store/store.html", context)


def cart(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("Product:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)
    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )
    return JsonResponse("Payment submitted..", safe=False)


def about(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/about.html", context)


def contact(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    products = Product.objects.all()
    thank = False
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        desc = request.POST.get("desc", "")
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    context = {"products": products, "cartItems": cartItems, "thank": thank}

    return render(request, "store/contact.html", context)


def search(request):
    if request.method == "POST":
        data = cartData(request)
        cartItems = data["cartItems"]
        products = Product.objects.all()
        # context = {}
        searched = request.POST["searched"]
        products_search = Product.objects.filter(category__contains=searched)
        return render(
            request,
            "store/search.html",
            {
                "searched": searched,
                "products_search": products_search,
                "products": products,
                "cartItems": cartItems,
            },
        )
    else:
        return render(request, "store/search.html")


def prodview(request, myid):
    data = cartData(request)
    cartItems = data["cartItems"]
    products = Product.objects.all()
    product = Product.objects.filter(id=myid)
    return render(
        request,
        "store/prod_view.html",
        {
            "product": product[0],
            "products": products,
            "cartItems": cartItems,
        },
    )
