from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from . forms import OrderForm
from . models import Order, Payment, OrderProduct
from accounts.models import Account
from carts.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
import datetime
import json

# Create your views here.






def paypal_payments(request):

    try:

        body = json.loads(request.body)
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    except:
        return HttpResponse('505 Not Found')  

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.status = 'Completed'
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        if item.variations.all():
             for variation in item.variations.all():
                  variation.variation_stock -= item.quantity
                  variation.save()
             
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)











def order_complete_paypal(request):

    
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        quantity = 0
        delivery_charges = 50
        # for i in ordered_products:
        #     subtotal += i.product_price * i.quantity

        for i in ordered_products:
             quantity += i.quantity
             if i.variations.all():
                  for variation in i.variations.all():
                        subtotal += (variation.variation_price * i.quantity)
             else:
                 subtotal += (i.product.price * i.quantity) 


        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'delivery_charges': delivery_charges,
        }

        # Send order recieved email to customer
        mail_subject = 'Here is the invoice of your order'
        message = render_to_string('orders/invoice_email.html', {
            'user': request.user,
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'delivery_charges': delivery_charges,
            })
        
        to_emails = [request.user.email,'adukkalaorders@gmail.com']
        send_email = EmailMessage(mail_subject, message, to=to_emails)
        send_email.content_subtype = 'html'
        send_email.send()


        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')
    













import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET_KEY))



def place_order(request,total=0,quantity=0):
    
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')
    
    grand_total = 0
    # tax = 0
    # delivery_charges = 50
    # for cart_item in cart_items:
    #     total = (cart_item.product.price * cart_item.quantity)
    #     quantity += cart_item.quantity
    for cart_item in cart_items:
            quantity += cart_item.quantity
            if cart_item.variations.all():
                for variation in cart_item.variations.all():
                    total += (variation.variation_price * cart_item.quantity)
            else:
                 total += (cart_item.product.price * cart_item.quantity) 

    # tax = (2*total)/100
    grand_total = total #+ tax + delivery_charges


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.zipcode = form.cleaned_data['zipcode']
            data.payment_method = form.cleaned_data['payment_method']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            # data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context = {
                'order':order,
                'quantity':quantity,
                'cart_items':cart_items,
                'total':total,
                # 'tax':tax,
                # 'delivery_charges':delivery_charges,
                'grand_total':grand_total
            }

            if data.payment_method == 'paypal':
                return render(request,'orders/paypal_payments.html',context)
            
            if data.payment_method == 'razorpay':

                order_currency = 'INR'

                callback_url = 'http://'+str(get_current_site(request))+'/orders/razorpay_handlerequest/'
                notes = {'order-type':'basic order from the website'}
                razorpay_order = razorpay_client.order.create(dict(amount=grand_total*100,currency=order_currency,payment_capture='0',notes=notes,receipt=order.order_number))
                order.razorpay_order_id = razorpay_order['id']
                order.save()
                return render(request,'orders/razorpay_payments.html',{'order':order,'razorpay_order_id':razorpay_order['id'],'quantity':quantity,'cart_items':cart_items,'total':total,'grand_total':grand_total,'razorpay_merchant_id':settings.RAZORPAY_API_KEY,'callback_url':callback_url,'user':current_user})
            
            else:

                return render(request,'orders/cash_on_delivery.html',context)
    else:
        return redirect('checkout')




 




# @login_required(login_url = 'login')
@csrf_exempt
def razorpay_handlerequest(request):

        user_id = request.GET.get('user_id')
        current_user = Account.objects.get(id=user_id)
        
        if request.method == 'POST':
            try:
                payment_id = request.POST.get('razorpay_payment_id', '')
                razorpay_order_id = request.POST.get('razorpay_order_id', '')
                signature = request.POST.get('razorpay_signature', '')
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                }
                try:
                    
                    order = Order.objects.get(user=current_user, is_ordered=False, razorpay_order_id=razorpay_order_id)
                except: 
                    return HttpResponse('505 Not Found')     

                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.save()

                result = razorpay_client.utility.verify_payment_signature(params_dict)
            
                if result is not None:
                    amount = order.order_total * 100
                    try:
                        razorpay_client.payment.capture(payment_id, amount)
                        

                        # Store transaction details inside Payment model
                        payment = Payment(
                            user = current_user,
                            payment_id = payment_id,
                            payment_method = 'razorpay',
                            amount_paid = order.order_total,
                            status = 'success',
                        )
                        payment.save()

                        order.payment = payment
                        order.is_ordered = True
                        order.status = 'Completed'
                        order.save()

                        # Move the cart items to Order Product table
                        cart_items = CartItem.objects.filter(user=current_user)

                        for item in cart_items:
                            orderproduct = OrderProduct()
                            orderproduct.order_id = order.id
                            orderproduct.payment = payment
                            orderproduct.user_id = current_user.id
                            orderproduct.product_id = item.product_id
                            orderproduct.quantity = item.quantity
                            orderproduct.product_price = item.product.price
                            orderproduct.ordered = True
                            orderproduct.save()

                            cart_item = CartItem.objects.get(id=item.id)
                            product_variation = cart_item.variations.all()
                            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                            orderproduct.variations.set(product_variation)
                            orderproduct.save()


                            # Reduce the quantity of the sold products
                            product = Product.objects.get(id=item.product_id)
                            product.stock -= item.quantity
                            if item.variations.all():
                                for variation in item.variations.all():
                                    variation.variation_stock -= item.quantity
                                    variation.save()
                                
                            product.save()

                        # Clear cart
                        CartItem.objects.filter(user=current_user).delete()

                        # Send order recieved email to customer
                        mail_subject = 'Thank you for your order!'
                        message = render_to_string('orders/order_recieved_email.html', {
                            'user': current_user,
                            'order': order,
                        })
                        to_email = current_user.email
                        send_email = EmailMessage(mail_subject, message, to=[to_email])
                        send_email.send()

                        
                        order_number = order.order_number
                        transID = payment.payment_id
                        return redirect('order_complete_razorpay', order_number=order_number, transID=transID)
                    
                    except:
                        # Store transaction details inside Payment model
                        payment = Payment(
                            user = current_user,
                            payment_id = payment_id,
                            payment_method = 'razorpay',
                            amount_paid = order.order_total,
                            status = 'failed',
                        )
                        payment.save()
                        
                        order.status = 'Cancelled'
                        order.save()
                        return render(request,'orders/paymentfailed.html')
                else:
                    # Store transaction details inside Payment model
                    payment = Payment(
                            user = current_user,
                            payment_id = payment_id,
                            payment_method = 'razorpay',
                            amount_paid = order.order_total,
                            status = 'failed',
                        )
                    payment.save()
                        
                    order.status = 'Cancelled'
                    order.save()
                    return render(request,'orders/paymentfailed.html')
            except:
                payment = Payment(
                            user = current_user,
                            payment_id = payment_id,
                            payment_method = 'razorpay',
                            amount_paid = order.order_total,
                            status = 'failed',
                        )
                payment.save()
                        
                order.status = 'Cancelled'
                order.save()
                return render(request,'orders/paymentfailed.html')            










def order_complete_razorpay(request, order_number=None, transID=None):

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        quantity = 0
        # delivery_charges = 50
        # for i in ordered_products:
        #     subtotal += i.product_price * i.quantity

        for i in ordered_products:
             quantity += i.quantity
             if i.variations.all():
                  for variation in i.variations.all():
                        subtotal += (variation.variation_price * i.quantity)
             else:
                 subtotal += (i.product.price * i.quantity) 


        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            # 'delivery_charges': delivery_charges,
        }

        # Send order recieved email to customer
        mail_subject = 'Here is the invoice of your order'
        message = render_to_string('orders/invoice_email.html', {
            'user': request.user,
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            # 'delivery_charges': delivery_charges,
            })
        
        to_emails = [request.user.email,'adukkalaorders@gmail.com']
        send_email = EmailMessage(mail_subject, message, to=to_emails)
        send_email.content_subtype = 'html'
        send_email.send()


        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')













def cash_on_delivery(request,user_id,order_number):

    if request.method == 'POST':

        try:

            current_user = Account.objects.get(id=user_id)
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

        except:
            return HttpResponse('505 Not Found')  

        # Store transaction details inside Payment model
        payment = Payment(
            user = current_user,
            payment_id = 'NO',
            payment_method = 'cash_on_delivery',
            amount_paid = order.order_total,
            status = 'success',
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.status = 'Completed'
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=current_user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = current_user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()


            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            if item.variations.all():
                for variation in item.variations.all():
                    variation.variation_stock -= item.quantity
                    variation.save()
                
            product.save()

        # Clear cart
        CartItem.objects.filter(user=current_user).delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': current_user,
            'order': order,
        })
        to_email = current_user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        
                        
        return redirect('order_complete_cash_on_delivery', order_number=order_number)
    else:
        return HttpResponse('505 Not Found')










def order_complete_cash_on_delivery(request,order_number):

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        quantity = 0
        # delivery_charges = 50
        # for i in ordered_products:
        #     subtotal += i.product_price * i.quantity

        for i in ordered_products:
             quantity += i.quantity
             if i.variations.all():
                  for variation in i.variations.all():
                        subtotal += (variation.variation_price * i.quantity)
             else:
                 subtotal += (i.product.price * i.quantity) 


        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'subtotal': subtotal,
            # 'delivery_charges': delivery_charges,
        }

        # Send order recieved email to customer
        mail_subject = 'Here is the invoice of your order'
        message = render_to_string('orders/invoice_email.html', {
            'user': request.user,
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'subtotal': subtotal,
            # 'delivery_charges': delivery_charges,
            })
        
        to_emails = [request.user.email,'adukkalaorders@gmail.com']
        send_email = EmailMessage(mail_subject, message, to=to_emails)
        send_email.content_subtype = 'html'
        send_email.send()


        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('index')








