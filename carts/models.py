from django.db import models
from store.models import Product,Variation
from accounts.models import Account

# Create your models here.


class Cart(models.Model):

    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    


class CartItem(models.Model):

    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    # adding this field after including variations many products can have many variations so manytomany
    variations = models.ManyToManyField(Variation,blank=True) 
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True) 
    quantity = models.IntegerField() 
    is_active = models.BooleanField(default=True) 

    # def sub_total(self):
    #     return self.product.price * self.quantity
    #     # return self.variations.variation_price * self.quantity

    def sub_total(self):

        subtotal = 0
       
        if self.variations.all():
            # Add variation prices if any
            for variation in self.variations.all():
                subtotal += variation.variation_price * self.quantity
        else:
             subtotal = self.product.price * self.quantity


        return subtotal


    def __unicode__(self):
        return self.product
