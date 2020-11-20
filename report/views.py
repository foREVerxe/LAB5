from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.http import JsonResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import connection

from report.models import *
import json

# Create your views here.
def index(request):
    return render(request, 'report/base_report.html')

def ReportListAllInvoices(request):
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT i.invoice_no as "Invoice No", i.date as "Date" '
                        ' , i.customer_code as "Customer Code", c.name as "Customer Name" '
                        ' , i.due_date as "Due Date", i.total as "Total", i.vat as "VAT", i.amount_due as "Amount Due" '
                        ' , ili.product_code as "Product Code", p.name as "Product Name" '
                        ' , ili.quantity as "Quantity", ili.unit_price as "Unit Price", ili.extended_price as "Extended Price" '
                        ' FROM invoice i JOIN customer c ON i.customer_code = c.customer_code '
                        '  JOIN invoice_line_item ili ON i.invoice_no = ili.invoice_no '
                        '  JOIN product p ON ili.product_code = p.code ')
                            
        row = dictfetchall(cursor)
        column_name = [col[0] for col in cursor.description]

    data_report = dict()
    data_report['data'] = row
    data_report['column_name'] = column_name

    return render(request, 'report/report_list_all_invoices.html', data_report)

def ReportProductsSold(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT ili.product_code as "Product Code", p.name as "Product Name" '
                        ' , SUM(ili.quantity) as "Total Quantity Sold", SUM(ili.extended_price) as "Total Value Sold" '
                        ' FROM invoice i JOIN invoice_line_item ili ON i.invoice_no = ili.invoice_no '
                        '   JOIN product p ON ili.product_code = p.code '
                        ' GROUP BY p.code, ili.product_code, p.name ')
        
        row = dictfetchall(cursor)
        column_name = [col[0] for col in cursor.description]

    data_report = dict()
    data_report['data'] = row
    data_report['column_name'] = column_name

    return render(request, 'report/report_products_sold.html', data_report)

def ReportListAllProducts(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT code as "Code", name as "Name", units as "Units" FROM product ')
        
        row = dictfetchall(cursor)
        column_name = [col[0] for col in cursor.description]

    data_report = dict()
    data_report['data'] = row
    data_report['column_name'] = column_name

    return render(request, 'report/report_list_all_products.html', data_report)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [name[0].replace(" ", "_").lower() for name in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def CursorToDict(data,columns):
    result = []
    fieldnames = [name.replace(" ", "_").lower() for name in columns]
    for row in data:
        rowset = []
        for field in zip(fieldnames, row):
            rowset.append(field)
        result.append(dict(rowset))
    return result

def ReportListAllReceipt(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT r.receipt_no as "Receipt No", r.date as "Receipt Date" '
                                       ' , r.customer_code as "Customer Code", r.payment_code as "Payment Method" '
                                       ' , r.payment_ref as "Payment Reference", r.remark as "Remarks" '
                                       ' , r.total_received as "Total Received", c.name as "Customer Name" '
                                       ' , rli.invoice_no as "Invoice No", rli.amount_paid_here as "Amount Paid Here" '
                                       ' , i.date as "Invoice Date" '
                                       
                                       ' FROM receipt r JOIN customer c ON r.customer_code = c.customer_code '
                                       '  Join receipt_line_item rli ON r.receipt_no = rli.receipt_no'
                                       '  Join invoice i ON rli.invoice_no = i.invoice_no')
        
        row = dictfetchall(cursor)
        column_name = [col[0] for col in cursor.description]
    data_report = dict()
    data_report['data'] = row
    data_report['column_name'] = column_name

    return render(request, 'report/report_list_all_receipt.html', data_report)




def ReportUnpaidInvoice(request):
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT "Invoice No", i.date as "Invoice Date" '
		                     '  , c.name as "Customer Name", i.amount_due AS "Invoice Amount Due" '
		                     '  , "Invoice Amount Received", i.amount_due - "Invoice Amount Received" AS "Invoice Amount Not Paid" '
                             ' FROM( SELECT rli.invoice_no as "Invoice No", SUM(rli.amount_paid_here) as "Invoice Amount Received" '
	                         '  FROM receipt_line_item as rli '
	                         '  GROUP BY rli.invoice_no ) as li '
                             '  JOIN invoice as i '
	                         '   ON li."Invoice No" = i.invoice_no '
                             ' INNER JOIN customer as c '
	                         '   ON i.customer_code = c.customer_code')
        row1 = dictfetchall(cursor)
        column_name1 = [col[0] for col in cursor.description]
        cursor.execute        ('SELECT SUM(i.amount_due - "Invoice Amount Received") AS "Total invoice amount not paid", COUNT(li) AS "Number of Invoice not paid" '
                        
                    ' FROM(SELECT rli.invoice_no AS "Invoice No", SUM(rli.amount_paid_here) as "Invoice Amount Received" '
                            ' FROM receipt_line_item as rli '
                            ' GROUP BY rli.invoice_no )as li '
                        ' INNER JOIN invoice as i '
                            ' ON li."Invoice No" = i.invoice_no '
                        ' WHERE i.amount_due - "Invoice Amount Received" !=  0 ')
        row2 = dictfetchall(cursor)        
        
    
    data_report = dict()
    data_report['data'] = row1
    data_report['column_name'] = column_name1
    data_report['data2'] = row2
    return render(request, 'report/report_unpaid_invoice.html', data_report)


