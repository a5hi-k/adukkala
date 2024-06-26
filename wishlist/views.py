from django.shortcuts import render,redirect
from store.models import Product
from . models import Wishlist,WishlistItem
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.



# private function
def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist  




def add_wishlist(request,product_id):


    current_user = request.user

    product = Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:

        

        

        is_wishlist_item_exists = WishlistItem.objects.filter(product=product,user=current_user).exists()

        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product,user=current_user)
            
            wishlist_item.delete()

        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                user = current_user,
            )
            
            wishlist_item.save()

        return redirect('wishlist')

    # if the user is not authenticated
    else:
        
        try:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(
                wishlist_id = _wishlist_id(request)
            )    
        wishlist.save()
        


        is_wishlist_item_exists = WishlistItem.objects.filter(product=product,wishlist=wishlist).exists()

        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product,wishlist=wishlist)
            
            wishlist_item.delete()
        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                wishlist = wishlist,
            )
           
            wishlist_item.save()

        return redirect('wishlist')


           



def wishlist(request):
    wishlist_items = []
    try:
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user=request.user,is_active=True)
        else:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist,is_active=True)
    except ObjectDoesNotExist:
        pass        
                 
    context = {
        'wishlist_items':wishlist_items,
    }

    return render(request,'store/wishlist.html',context)

