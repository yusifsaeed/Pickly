from django.db import models
from django.contrib.auth.models import User
# this model contains username, email, password...

# Create your models here.

# Customer model
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)  
    second_name = models.CharField(max_length=100) 
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.second_name}"

 
# Category model
class Category(models.Model):
    category_name = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, blank=True)  
    image = models.ImageField(upload_to='categories/', blank=True, null=True) 
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = 'No Image Found'
        return url
    
    def __str__(self):   # special method
        return self.category_name
    
    class Meta:
        verbose_name_plural = "Categories"


# Product model
class Product(models.Model):
    name = models.CharField(max_length=200)  
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # this is to link product_category with catogires , if we delete all product del
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)  

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.name


# Order model
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True, null = True)
    order_date = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    trasaction_id = models.CharField(max_length=100, null= True)

    @property
    def cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.product_total_price for item in orderitems])
        return total 
    @property
    def cart_items_count(self):
        orderitems = self.orderitem_set.all()
        count = sum([item.quantity for item in orderitems])
        return count
    
    def __str__(self):
        return str(self.id)

# Order item

class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, blank=True, null = True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default= 0,blank=True, null = True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def product_total_price(self):
        if self.product:
            total = self.product.price * self.quantity
            return total
        return 0
    
    def check_quantity(self):
        if self.quantity > Product.quantity:
                return False
        return True

    
    def __str__(self):
        return f"{self.quantity}x {self.product.name if self.product else 'No Product'}"


# Shipping model 
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200)  
    city = models.CharField(max_length=200)  
    state = models.CharField(max_length=200)  
    zipcode = models.CharField(max_length=200) 
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    
    class Meta:
        verbose_name_plural = "Shipping Addresses"

#wishlist model

class favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"