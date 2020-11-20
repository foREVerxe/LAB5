from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.db.models import Max
from django.db import connection
from receipt.models import *
import json

# Create your views here.
def index(request):
    data = {}
    return render(request, 'receipt/receipt.html', data)

class CustomerList(View):
    def get(self, request):
        customers = list(Customer.objects.all().values())
        data = dict()
        data['customers'] = customers
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

class CustomerDetail(View):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        data = dict()
        data['customers'] = model_to_dict(customer)
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

class PaymentMethodList(View):
    def get(self, request):
        paymentMethods = list(PaymentMethod.objects.all().values())
        data = dict()
        data['paymentMethods'] = paymentMethods
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

class ReceiptList(View):
    def get(self, request):
        receipts = list(Receipt.objects.order_by('receipt_no').all().values())
        data = dict()
        data['receipts'] = receipts
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

class ReceiptDetail(View):
    def get(self, request, pk, pk2):
        receipt_no = pk + "/" + pk2
        receipt = list(Receipt.objects.select_related("custome").filter(receipt_no=receipt_no).values('receipt_no', 'customer_code', 'customer_code__name', 'date', 'payment_code', 'payment_code__name', 'payment_ref','total_received','remark'))
        receiptlineitem = list(ReceiptLineItem.objects.select_related('invoice_no').filter(receipt_no=receipt_no).order_by('lineitem').values("lineitem","receipt_no","invoice_no","invoice_no__date","invoice_no__amount_due","amount_paid_here"))

        data = dict()
        data['receipt'] = receipt[0]
        data['receiptlineitem'] = receiptlineitem

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = '__all__'

class ReceiptLineItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptLineItem
        fields = '__all__'

@method_decorator(csrf_exempt, name='dispatch')
class ReceiptCreate(View):
    def post(self, request):
        data = dict()
        request.POST = request.POST.copy()

        if Receipt.objects.count() != 0:
            receipt_no_max = Receipt.objects.aggregate(Max('receipt_no'))['receipt_no__max']
            next_receipt_no = receipt_no_max[0:3] + str(int(receipt_no_max[3:7])+1) + "/" + (receipt_no_max[8:])
        else:
            next_receipt_no = "RCT1000/20"
        request.POST['receipt_no'] = next_receipt_no
        request.POST['date'] = reFormatDateMMDDYYYY(request.POST['date'])
        request.POST['total_received'] = reFormatNumber(request.POST['total_received'])

        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save()

            dict_lineitem = json.loads(request.POST['lineitem'])
            for lineitem in dict_lineitem['lineitem']:
                lineitem['receipt_no'] = next_receipt_no
                lineitem['amount_paid_here'] = reFormatNumber(lineitem['amount_paid_here'])

                formlineitem = ReceiptLineItemForm(lineitem)
                formlineitem.save()

            data['receipt'] = model_to_dict(receipt)
        else:
            data['error'] = 'form not valid!'

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        
        return response

@method_decorator(csrf_exempt, name='dispatch')
class ReceiptUpdate(View):
    def post(self, request, pk, pk2):
        receipt_no = pk + "/" + pk2
        data = dict()
        receipt = Receipt.objects.get(pk=receipt_no)
        request.POST = request.POST.copy()
        request.POST['receipt_no'] = receipt_no
        request.POST['date'] = reFormatDateMMDDYYYY(request.POST['date'])
        request.POST['total_received'] = reFormatNumber(request.POST['total_received'])
        print(request.POST)
        form = ReceiptForm(instance=receipt, data=request.POST)
        if form.is_valid():
            receipt = form.save()

            ReceiptLineItem.objects.filter(receipt_no=receipt_no).delete()
            
            dict_lineitem = json.loads(request.POST['lineitem'])
            for lineitem in dict_lineitem['lineitem']:
                lineitem['receipt_no'] = receipt_no
                lineitem['amount_paid_here'] = reFormatNumber(lineitem['amount_paid_here'])

                formlineitem = ReceiptLineItemForm(lineitem)
                formlineitem.save()

            data['receipt'] = model_to_dict(receipt)
        else:
            data['error'] = 'form not valid!'

        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        
        return response

@method_decorator(csrf_exempt, name='dispatch')
class ReceiptDelete(View):
    def post(self, request, pk, pk2):
        receipt_no = pk + "/" + pk2
        data = dict()
        receipt = Receipt.objects.get(pk=receipt_no)
        if receipt:
            receipt.delete()
            data['message'] = "Invoice Deleted!"
        else:
            data['message'] = "Error!"

        return JsonResponse(data)

class ReceiptPDF(View):
    def get(self, request, pk, pk2):
        receipt_no = pk + "/" + pk2

        receipt = list(Receipt.objects.select_related("custome").filter(receipt_no=receipt_no).values('receipt_no', 'customer_code', 'customer_code__name', 'date', 'payment_code', 'payment_code__name', 'payment_ref','total_received','remark'))
        receiptlineitem = list(ReceiptLineItem.objects.select_related('invoice_no').filter(receipt_no=receipt_no).order_by('lineitem').values("lineitem","receipt_no","invoice_no","invoice_no__date","invoice_no__amount_due","amount_paid_here"))
        #invoicelineitem = InvoiceLineItem.objects.raw(
        #    "SELECT * "
        #    "FROM invoice_line_item LIT "
        #    "  JOIN product P ON LIT.product_code = P.code "
        #    "WHERE LIT.invoice_no = '{}'" .format(invoice_no)
        #)

        #list_lineitem = [] 
        #for lineitem in invoicelineitem:
        #    dict_lineitem = json.loads(str(lineitem))
        #    dict_lineitem['product_name'] = lineitem.product_code.name
        #    dict_lineitem['units'] = lineitem.product_code.units
        #    list_lineitem.append(dict_lineitem)

        for line in receiptlineitem:
            line['iar'] = line['invoice_no__amount_due'] - line['amount_paid_here']
        print(receiptlineitem)
        data = dict()
        data['receipt'] = receipt[0]
        data['receiptlineitem'] = receiptlineitem
        
        #return JsonResponse(data)
        return render(request, 'receipt/pdf.html', data)

class ReceiptReport(View):
    def get(self, request):

        with connection.cursor() as cursor:
            cursor.execute('SELECT r.receipt_no as "Receipt No", r.date as "Receipt Date" '
                           ' , r.customer_code as "Customer Code", c.name as "Customer Name" '
                           ' , pm.name as "Payment Method" '
                           ' , r.payment_ref as "Payment Ref", r.total_received as "Total received", r.remark as "Remark" '
                           ' FROM receipt r '
                           ' LEFT JOIN customer c '
                           '    ON r.customer_code = c.customer_code '
                           ' LEFT JOIN payment_method pm '
                           '    ON r.payment_code = pm.code '
                           ' ORDER BY r.receipt_no '
                           )
            
            row = dictfetchall(cursor)
            column_name = [col[0] for col in cursor.description]

        data = dict()
        data['column_name'] = column_name
        data['data'] = row
        
        #return JsonResponse(data)
        return render(request, 'receipt/report.html', data)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [name[0].replace(" ", "_").lower() for name in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def reFormatDateMMDDYYYY(ddmmyyyy):
        if (ddmmyyyy == ''):
            return ''
        return ddmmyyyy[3:5] + "/" + ddmmyyyy[:2] + "/" + ddmmyyyy[6:]

def reFormatNumber(str):
        if (str == ''):
            return ''
        return str.replace(",", "")