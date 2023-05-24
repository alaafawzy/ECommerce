from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from .forms import *
from .models import *

def product_stock(product_id):
    purchase_item_list = PurchaseOrderItem.objects.all()
    sales_item_list = SalesOrderItem.objects.all()

    count = 0
    for purchase_item in purchase_item_list:
        if purchase_item.product.id == product_id:
            count += purchase_item.quantity
        
    for sales_item in sales_item_list:
        if sales_item.product.id == product_id:
            count -= sales_item.quantity
    
    return count

def items_in_cart(id):
    sales_item_list = SalesOrderItem.objects.all()
    items_in_cart = 0 
        
    for sales_item in sales_item_list:
        if sales_item.sale_order.user.id == id:
            items_in_cart += sales_item.quantity
    
    return items_in_cart


class DetailsPage(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'ShoppingCartAdmin/DetailsPage.html', {
            'product': request.product,
            'imge_list': UploadProductImage.objects.all(),
        }
        )


class LoginPage(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'ShoppingCartAdmin/Login.html', {'form':LoginForm})

    def post(self, request):
        data = LoginForm(request.POST)
        if data.is_valid():
            username = data.cleaned_data.get('username')
            password = data.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
        
        return render(request, 'ShoppingCartAdmin/Login.html', {'form':LoginForm})


class RegisterPage(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'ShoppingCartAdmin/Register.html', {
            'register_form': RegisterForm,
            'address_form': AddressForm,
        })
    
    def post(self, request):
        if request.method=='POST':
            # if address
            if 'address' in request.POST:
                data = AddressForm(request.POST)
                if data.is_valid():
                    street = data.cleaned_data.get('street')
                    city = data.cleaned_data.get('city')
                    postal_code = data.cleaned_data.get('postal_code')
                    address_type = data.cleaned_data.get('address_type')

                    address = Address.objects.create(street=street, city=city, postal_code=postal_code, address_type=address_type)
            
            elif 'register' in request.POST:
                data = RegisterForm(request.POST)
                if data.is_valid():
                    user = data.save()
                    login(request, user)
                    return redirect('homepage')
        
        return render(request, 'ShoppingCartAdmin/Register.html', {
            'register_form': RegisterForm,
            'address_form': AddressForm,
        })


def get_list(user_id):
    items_list = Product.objects.all()
    purchase_item_list = PurchaseOrderItem.objects.all()
    sales_item_list = SalesOrderItem.objects.all()
    list = []

    for item in items_list:
        count = 0
        for sale in sales_item_list:
            if sale.product.id == item.id:
                if sale.sale_order.user.id == user_id:
                    count += sale.quantity
            
        list.append((item, count))
    
    return list


class CartPage(generic.View):
    def get(self, request, *args, **kwargs):
        list = get_list(request.user.id)
        
        return render(request, 'ShoppingCartAdmin/Cart.html', {
            'list': list,
            'form': CartUpdate,
        })
    
    def post(self, request):
        if request.method == 'POST':
            data = CartUpdate(request.POST)
            if data.is_valid():
                update_quantity = data.cleaned_data.get('update_quantity')
                if update_quantity < 0:
                    list = get_list(request.user.id)
                    return render(request, 'ShoppingCartAdmin/Cart.html', {
                        'list': list,
                        'form': CartUpdate,
                    })
                
                pro = None
                items = Product.objects.all();
                for item in items:
                    if str(item.id) in request.POST:
                        pro = item
                

                max_quantity = 0 
                for purchase in PurchaseOrderItem.objects.all():
                    if purchase.product.id == pro.id:
                        max_quantity += purchase.quantity

                if update_quantity > max_quantity:
                    list = get_list(request.user.id)
                    return render(request, 'ShoppingCartAdmin/Cart.html', {
                        'list': list,
                        'form': CartUpdate,
                    })

                for sale in SalesOrderItem.objects.all():
                    if sale.product.id == pro.id:
                        update_quantity -= sale.quantity
                
                for sale in SalesOrderItem.objects.all():
                    if sale.sale_order.user.id==request.user.id and sale.product.id == pro.id:
                        if update_quantity < 0:
                            rmv = -1*update_quantity
                            if sale.quantity < rmv:
                                rmv = sale.quantity

                            sale.quantity -= rmv 
                            update_quantity += rmv 
                            sale.save()
                        
                        elif update_quantity > 0:
                            sale.quantity += update_quantity
                            update_quantity = 0 
                            sale.save()


        list = get_list(request.user.id)
        return render(request, 'ShoppingCartAdmin/Cart.html', {
            'list': list,
            'form': CartUpdate,
        })

    


class HomePage(generic.View):
    def get(self, request, *args, **kwargs):
        print(request.user)
        if request.user.id is not None:
            return render(request, 'ShoppingCartAdmin/HomePage.html', {
                'login': 'True',
                'cart_items': items_in_cart(request.user.id),
                'products': Product.objects.all(),
            })
        
        else:
            return render(request, 'ShoppingCartAdmin/HomePage.html', {
                'login': 'False',
                'products': Product.objects.all(),
            })

    
    def post(self, request):
        if request.method=='POST':
            # if login
            if 'login' in request.POST:
                return redirect('loginpage')

            # if logout
            elif 'logout' in request.POST:
                logout(request)
                return render(request, 'ShoppingCartAdmin/HomePage.html', {
                    'login': 'False',
                    'products': Product.objects.all(),
                })

            # if register
            elif 'register' in request.POST:
                return redirect('registerpage')
            
            elif 'cart' in request.POST:
                return redirect('cartpage')

            else:
                # if product details
                item_list = Product.objects.all()
                for item in item_list:
                    cur_detail_name = "Details + " + str(item.id)
                    cur_add_name = "Add + " + str(item.id)

                    if cur_detail_name in request.POST:
                        return render(request, 'ShoppingCartAdmin/DetailsPage.html',{
                            'product': item,
                            'imge_list': UploadProductImage.objects.all(),
                        })
                    
                    elif cur_add_name in request.POST:
                        print("add item to cart")
                        print(product_stock(item.id))
                        if product_stock(item.id) > 0:
                            print("here\n")
                            order = SalesOrder.objects.create(user = request.user)
                            order_item = SalesOrderItem.objects.create(
                                product = item, quantity = 1, sale_order = order
                            )
                        
                        return render(request, 'ShoppingCartAdmin/HomePage.html', {
                            'login': 'True',
                            'cart_items': items_in_cart(request.user.id),
                            'products': Product.objects.all(),
                        })
        

        if request.user.id is not None:
            return render(request, 'ShoppingCartAdmin/HomePage.html', {
                'login': 'True',
                'cart_items': items_in_cart(request.user.id),
                'products': Product.objects.all(),
            })
        
        else:
            return render(request, 'ShoppingCartAdmin/HomePage.html', {
                'login': 'False',
                'products': Product.objects.all(),
            })
