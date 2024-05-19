
from django.urls import path
from . import views

urlpatterns = [
   
    path('place_order/',views.place_order,name='place_order'),
    path('paypal_payments/',views.paypal_payments,name='paypal_payments'),
    path('razorpay_handlerequest/',views.razorpay_handlerequest,name='razorpay_handlerequest'),
    path('order_complete_paypal/', views.order_complete_paypal, name='order_complete_paypal'),
    path('order_complete_razorpay/<int:order_number>/<str:transID>/', views.order_complete_razorpay, name='order_complete_razorpay'),
    path('cash_on_delivery/<int:user_id>/<int:order_number>/',views.cash_on_delivery,name='cash_on_delivery'),
    path('order_complete_cash_on_delivery/<int:order_number>/',views.order_complete_cash_on_delivery,name='order_complete_cash_on_delivery')
] 
