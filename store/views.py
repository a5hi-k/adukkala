from django.shortcuts import render,get_object_or_404,redirect
from . models import Product   #ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from . models import ReviewRating
from . forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.

def store(request,category_slug=None):

    category = None
    products = None

    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category,is_available=True).order_by('-created_date')
        paginator = Paginator(products,15)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        tot_prod_count = products.count()
        if paged_products.number == 1:
            start_item_number = 1
        else:
            start_item_number = (paged_products.number - 1) * paged_products.paginator.per_page + 1

        end_item_number = start_item_number + len(paged_products) - 1
    else:
        products = Product.objects.filter(is_available=True).order_by('-created_date')
        paginator = Paginator(products,15)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        tot_prod_count = products.count()
        if paged_products.number == 1:
            start_item_number = 1
        else:
            start_item_number = (paged_products.number - 1) * paged_products.paginator.per_page + 1

        end_item_number = start_item_number + len(paged_products) - 1



    categories = Category.objects.all()

    context = {
        'products': paged_products,
        'categories': categories,
        'tot_prod_count':tot_prod_count,
        'start': start_item_number,
        'end' : end_item_number,
        
    }

    return render(request,'store/store.html',context)



def product_detail(request,category_slug,product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        # cart__ is used since cart is the foreignkey in CartItem
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
            
        except OrderProduct.DoesNotExist: 
            orderproduct = None  

    else:
        orderproduct = None


    reviews = ReviewRating.objects.filter(product_id=single_product.id,status=True)
    reviews_count = len(reviews) 

    # Get the product gallery if it its model is created
    # product_gallery = ProductGallery .objects.filter(product_id=single_product.id)  

    related_products = Product.objects.filter(category=single_product.category).order_by('-created_date').exclude(id=single_product.id)[:4]
    
        
    context ={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'reviews_count':reviews_count,
        'related_products':related_products,
        # 'product_gallery':product_gallery,

    }
    
    return render(request, 'store/product_detail.html',context)





def search(request):

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword) | Q(category__category_name__icontains=keyword) | Q(product_brand__icontains=keyword))
            tot_prod_count = products.count()
            end = tot_prod_count
            start = 1
            
    context = {
        'products':products,
        'tot_prod_count':tot_prod_count,
        'start':start,
        'end':end,
        
    }         
     
    return render(request,'store/store.html',context)
     
     



def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            # instance is add to rewrite the current insted of creating new if it exist
            form =ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,'Thank you! Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()

                messages.success(request,'Thank you! Your review has been submitted')
                return redirect(url)





def offer_products(request):
    offer_products = Product.objects.all().filter(is_available=True,offer_product=True).order_by('-created_date')
    context={
        'offer_products':offer_products
    }
    return render(request,'store/offer_products.html',context)





def compare_select(request,product1_id):
    product1 = Product.objects.get(id=product1_id)
    category = product1.category.category_name
    comparing_products = Product.objects.all().filter(category__category_name__icontains=category,is_available=True).exclude(id=product1_id)

    reviews = ReviewRating.objects.filter(product_id=product1.id,status=True)
    reviews_count = len(reviews) 

    context = {
        'product1':product1,
        'products':comparing_products,
        'reviews':reviews,
        'reviews_count':reviews_count,
    }
    return render(request,'store/compare_select.html',context)







def compare(request,product1_id,product2_id):
    product1 = Product.objects.get(id=product1_id)
    product2 = Product.objects.get(id=product2_id)
    
    reviews1 = ReviewRating.objects.filter(product_id=product1.id,status=True)
    reviews_count1 = len(reviews1) 

    reviews2 = ReviewRating.objects.filter(product_id=product2.id,status=True)
    reviews_count2 = len(reviews2) 

    context = {
        'product1':product1,
        'product2':product2,
        'reviews1':reviews1,
        'reviews_count1':reviews_count1,
        'reviews2':reviews2,
        'reviews_count2':reviews_count2,
    }
    return render(request,'store/compare.html',context)