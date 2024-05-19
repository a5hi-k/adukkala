from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg,Count
# Create your models here.


class Product(models.Model):
    offer_product=models.BooleanField(default=False)
    product_name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    product_description =  models.TextField(max_length=1000)
    product_brand = models.CharField(max_length=20, null=True, blank=True)
    MRP_price = models.IntegerField()
    best_seller = models.BooleanField(default=False)
    price = models.IntegerField()
    product_image = models.ImageField(upload_to='images/products')
    product_image_big1 = models.ImageField(upload_to='images/products',blank=True, null=True)
    product_image_big2 = models.ImageField(upload_to='images/products',blank=True, null=True)
    model3d = models.FileField(upload_to='3d_objects', null=True, blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.product_name
    

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg    
    

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count   
    




# this is done for getting the variation values separately
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)




variation_category_choice = (
    ('size','size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)  
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    variation_price = models.IntegerField(null=True,blank=True) # if null then it will take from product price 
    variation_MRP_price = models.IntegerField()
    variation_stock = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)



    def save(self, *args, **kwargs):
        # Set default value for variation_price if not provided
        if not self.variation_price:
            self.variation_price = self.product.price  # Assuming product has a price field
        super().save(*args, **kwargs)



    # this should be give after writing the above class VariationManager
    objects = VariationManager()

    # def __unicode__(self):
    #     return self.product

    # done of displaying the dynamic variation values
    def __str__(self):
        return self.variation_value
    





class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review = models.TextField(max_length=700,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject






# class ProductGallery(models.Model):
#     product = models.ForeignKey(Product,default=None,on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='store/products',max_length=255)

#     def __str__(self):
#         return self.product.product_name

#     class Meta:
#         verbose_name = 'productgallery'
#         verbose_name_plural = 'product gallery'





class Advertisement(models.Model):
    name = models.CharField(max_length=100)
    ad_image = models.ImageField(upload_to='images/advertisements')
    created_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name