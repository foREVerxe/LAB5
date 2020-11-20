from django.contrib import admin

# Register your models here.
from .models import Product
from .models import Customer
from .models import Invoice
from .models import InvoiceLineItem

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InvoiceLineItem)