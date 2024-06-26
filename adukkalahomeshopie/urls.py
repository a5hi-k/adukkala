"""
URL configuration for adukkalahomeshopie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('adukkalasecureadminlogin@gigi/', admin.site.urls),
    path('',views.index,name='index'),
    path('store/',include('store.urls')),
    path('cart/',include('carts.urls')),
    path('wishlist/',include('wishlist.urls')),
    path('accounts/',include('accounts.urls')), #for user authentication
    path('about_us/',views.about_us,name='about_us'),
    # orders
    path('orders/',include('orders.urls')),

    # Chatbot message handler
    path('chatbot/', views.chatbot_message_handler, name='chatbot_message_handler'),

    # compare AI handler
    path('compare_ai/<int:product1_id>/<int:product2_id>/',views.compare_ai,name='compare_ai')
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
