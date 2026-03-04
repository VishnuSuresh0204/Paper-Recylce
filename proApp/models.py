from django.db import models
from django.utils.timezone import now


# Create your models here.
class Login(models.Model):
    email = models.EmailField(max_length=100, null=True)
    password = models.CharField(max_length=100, null=True)
    userType = models.CharField(max_length=100, null=True)

class UserReg(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=100)
    password = models.CharField(max_length=128)

class Organizer(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=100, null=True, default="pending")

class Collector(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE,null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    status = models.CharField(max_length=100, null=True, default="pending")
    idproof = models.ImageField(upload_to='proof/', blank=True, null=True) 
    
    

class WasteCollectionRequest(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    request_date = models.DateTimeField(default=now)
    address = models.TextField()
    house_number = models.CharField(max_length=50) 
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    waste_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    assign_status = models.CharField(max_length=50, default='Pending')
    collector = models.ForeignKey(Collector, on_delete=models.SET_NULL, null=True, blank=True)
    organizer = models.ForeignKey(Organizer, on_delete=models.SET_NULL, null=True, blank=True)
    reply_message = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    payment_status = models.CharField(max_length=20, default='Unpaid')   
    collector_payment_status = models.CharField(max_length=20, default='Pending')
    pickup_date = models.DateField(null=True, blank=True)


class RecycledProduct(models.Model):
    org = models.ForeignKey(Organizer, on_delete=models.CASCADE,null=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='productimages/', blank=True, null=True) 

class Order(models.Model):
    product = models.ForeignKey(RecycledProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    name = models.CharField(max_length=50,null=True)
    phone = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default='Pending')
    status = models.CharField(max_length=50, default='Pending')


class ProductReview(models.Model):
    product = models.ForeignKey(RecycledProduct, related_name='product_reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(UserReg, on_delete=models.CASCADE)
    feedback = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)



