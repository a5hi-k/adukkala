from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from . models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.




# private function
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart    




def add_cart(request,product_id):


    current_user = request.user

    product = Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:

        product_variation = []

        if request.method == 'POST':
            # size = request.POST['size']
            # color = request.POST['color']
            for item in request.POST:
                key = item
                value =  request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass    

        is_cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            # existing variations  -> database
            # current variations   -> product_variation
            # item_id              -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                # ---------------------------------------------------------------------
                # for handling stocks getting out of stock while adding to cart
                if not item.variations.all():
                    if (item.product.stock - item.quantity) > 0:
                        item.quantity +=1
                        item.save()
                    else:
                        messages.warning(request,"Product out of stock!")
                        return redirect('cart')  
                    
                else:
                    for variation in item.variations.all():
                        if (variation.variation_stock - item.quantity) > 0:
                            item.quantity += 1
                            item.save()
                        else:
                            messages.warning(request,"Product out of stock!")
                            return redirect('cart')     
                # ---------------------------------------------------------------------
                # item.quantity +=1
                # item.save()

            else:        
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

    # if the user is not authenticated
    else:


        product_variation = []

        if request.method == 'POST':
            # size = request.POST['size']
            # color = request.POST['color']
            for item in request.POST:
                key = item
                value =  request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass    

        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )    
        cart.save()
        


        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing variations  -> database
            # current variations   -> product_variation
            # item_id              -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                
                if not item.variations.all():
                    if (item.product.stock - item.quantity) > 0:
                        item.quantity +=1
                        item.save()
                    else:
                        messages.warning(request,"Product out of stock!")
                        return redirect('cart')  
                    
                else:
                    for variation in item.variations.all():
                        if (variation.variation_stock - item.quantity) > 0:
                            item.quantity += 1
                            item.save()
                        else:
                            messages.warning(request,"Product out of stock!")
                            return redirect('cart')    

            else:        
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')






def remove_cart(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
             cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))     
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
        
    return redirect("cart")




def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))    
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')





def cart(request,total=0,quantity=0,cart_items=None):
    try:
        # tax = 0
        
        MRP_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            if cart_item.variations.all():
                for variation in cart_item.variations.all():
                    total += (variation.variation_price * cart_item.quantity)
                    MRP_total += (variation.variation_MRP_price * cart_item.quantity)
            else:
                 total += (cart_item.product.price * cart_item.quantity)
                 MRP_total += (cart_item.product.MRP_price * cart_item.quantity)

        # tax = (2 * total)/100              
            
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'MRP_total':MRP_total,
        'cart_items':cart_items,
    }

    return render(request,'store/cart.html',context)





@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    # tax = 0
    grand_total = 0
    # delivery_charges = 50

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            quantity += cart_item.quantity
            if cart_item.variations.all():
                for variation in cart_item.variations.all():
                    total += (variation.variation_price * cart_item.quantity)
            else:
                 total += (cart_item.product.price * cart_item.quantity)

        # tax = (2 * total)/100
        grand_total = total # + tax + delivery_charges                
            
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total': grand_total,
    }

    return render(request,'store/checkout.html',context)



