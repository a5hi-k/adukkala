

from django.urls import path
from . import views

urlpatterns = [
   
    path('',views.store,name='store'),
    path('category/<slug:category_slug>/',views.store,name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
    path('search/',views.search , name='search'), 
    path('submit_review<int:product_id>/',views.submit_review,name="submit_review"),
    path('offer_products/',views.offer_products,name='offer_products'),
    path('compare_select/<int:product1_id>/',views.compare_select,name="compare_select"),
    path('compare/<int:product1_id>/<int:product2_id>/',views.compare,name="compare"),
    
] 
