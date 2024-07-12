from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.students.models import Student

from .forms import InvoiceItemFormset, InvoiceReceiptFormSet, Invoices
from .models import Invoice, InvoiceItem, Receipt


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = "__all__"
    success_url = "/finance/list"

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        if self.object.id != None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = ["student", "session", "term", "class_for", "balance_from_previous_term"]

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(
                self.request.POST, instance=self.object
            )
            context["items"] = InvoiceItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            context["receipts"] = InvoiceReceiptFormSet(instance=self.object)
            context["items"] = InvoiceItemFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
        return super().form_valid(form)


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        obj.invoice = invoice
        obj.save()
        return redirect("invoice-list")

    def get_context_data(self, **kwargs):
        context = super(ReceiptCreateView, self).get_context_data(**kwargs)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        context["invoice"] = invoice
        return context


class ReceiptUpdateView(LoginRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")


class ReceiptDeleteView(LoginRequiredMixin, DeleteView):
    model = Receipt
    success_url = reverse_lazy("invoice-list")


@login_required
def bulk_invoice(request):
    return render(request, "finance/bulk_invoice.html")




import csv


from django.http import HttpResponse


# class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

#         writer = csv.writer(response)
#         writer.writerow(
#             [
#                 "registration_number",
#                 "surname",
#                 "firstname1",
#                 "other_names1",
#                 "gender1",
#                 "parent_number1",
#                 "address1",
#                 "current_class",
#             ]
#         )

#         return response




######### downloading to word format:


# from django.shortcuts import get_object_or_404, HttpResponse
# from .models import Invoice, InvoiceItem, Receipt  # Adjust based on your actual models
# from docx import Document

# def download_invoice(request, invoice_id):
#     # Fetch invoice details
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     items = InvoiceItem.objects.filter(invoice=invoice)
#     receipts = Receipt.objects.filter(invoice=invoice)

#     # Create a new Document
#     doc = Document()
#     doc.add_heading(f'Invoice #{invoice.id}', level=1)

#     # Add invoice details in a 2-column table
#     table = doc.add_table(rows=5, cols=2)
#     table.style = 'Table Grid'

#     row = table.rows[0]
#     row.cells[0].text = 'Invoice'
#     row.cells[1].text = str(invoice)

#     row = table.rows[1]
#     row.cells[0].text = 'Session'
#     row.cells[1].text = str(invoice.session)

#     row = table.rows[2]
#     row.cells[0].text = 'Term'
#     row.cells[1].text = str(invoice.term)

#     row = table.rows[3]
#     row.cells[0].text = 'Class'
#     row.cells[1].text = str(invoice.class_for)

#     row = table.rows[4]
#     row.cells[0].text = 'Status'
#     row.cells[1].text = str(invoice.get_status_display())

#     doc.add_paragraph()

#     # Add Expected Balance
#     doc.add_paragraph(f'Expected Balance: {invoice.balance()}')

#     doc.add_paragraph()

#     # Add Invoice Breakdown table
#     doc.add_heading('Invoice Breakdown', level=1)
#     table = doc.add_table(rows=1, cols=3)
#     table.style = 'Table Grid'
#     hdr_cells = table.rows[0].cells
#     hdr_cells[0].text = 'S/N'
#     hdr_cells[1].text = 'Description'
#     hdr_cells[2].text = 'Amount'

#     for i, item in enumerate(items, start=1):
#         row_cells = table.add_row().cells
#         row_cells[0].text = str(i)
#         row_cells[1].text = item.description
#         row_cells[2].text = str(item.amount)

#     # Add totals
#     doc.add_paragraph(f'Total Amount this term: {invoice.amount_payable()}')
#     doc.add_paragraph(f'Balance from previous term: {invoice.balance_from_previous_term}')
#     doc.add_paragraph(f'Total Amount Payable: {invoice.total_amount_payable()}')
#     doc.add_paragraph(f'Total Amount Paid: {invoice.total_amount_paid()}')

#     doc.add_paragraph()

#     # Add Payment History
#     doc.add_heading('Payment History', level=1)
#     table = doc.add_table(rows=1, cols=4)
#     table.style = 'Table Grid'
#     hdr_cells = table.rows[0].cells
#     hdr_cells[0].text = 'S/N'
#     hdr_cells[1].text = 'Amount Paid'
#     hdr_cells[2].text = 'Date Paid'
#     hdr_cells[3].text = 'Comment'

#     for i, receipt in enumerate(receipts, start=1):
#         row_cells = table.add_row().cells
#         row_cells[0].text = str(i)
#         row_cells[1].text = str(receipt.amount_paid)
#         row_cells[2].text = receipt.date_paid.strftime('%Y-%m-%d')  # Format date as needed
#         row_cells[3].text = receipt.comment

#     # Save the document to a response
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
#     response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.docx'
#     doc.save(response)
#     return response



######## downloading to pdf format

# from django.shortcuts import get_object_or_404, HttpResponse
# from .models import Invoice, InvoiceItem, Receipt
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch

# def download_invoice(request, invoice_id):
#     # Fetch invoice details
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     items = InvoiceItem.objects.filter(invoice=invoice)
#     receipts = Receipt.objects.filter(invoice=invoice)

#     # Create a new PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'
#     p = canvas.Canvas(response, pagesize=A4)
#     width, height = A4

#     # Add invoice details
#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(1 * inch, height - 1 * inch, f'Invoice #{invoice.id}')

#     # Add invoice details in text
#     p.setFont("Helvetica", 12)
#     p.drawString(1 * inch, height - 1.5 * inch, f'Invoice: {invoice}')
#     p.drawString(1 * inch, height - 1.75 * inch, f'Session: {invoice.session}')
#     p.drawString(1 * inch, height - 2 * inch, f'Term: {invoice.term}')
#     p.drawString(1 * inch, height - 2.25 * inch, f'Class: {invoice.class_for}')
#     p.drawString(1 * inch, height - 2.5 * inch, f'Status: {invoice.get_status_display()}')

#     # Add Expected Balance
#     p.drawString(1 * inch, height - 3 * inch, f'Expected Balance: {invoice.balance()}')

#     # Add Invoice Breakdown
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, height - 3.5 * inch, 'Invoice Breakdown')
#     p.setFont("Helvetica", 12)
#     y_position = height - 4 * inch

#     for i, item in enumerate(items, start=1):
#         p.drawString(1 * inch, y_position, f'{i}. {item.description} - {item.amount}')
#         y_position -= 0.25 * inch

#     # Add totals
#     y_position -= 0.5 * inch
#     p.drawString(1 * inch, y_position, f'Total Amount this term: {invoice.amount_payable()}')
#     y_position -= 0.25 * inch
#     p.drawString(1 * inch, y_position, f'Balance from previous term: {invoice.balance_from_previous_term}')
#     y_position -= 0.25 * inch
#     p.drawString(1 * inch, y_position, f'Total Amount Payable: {invoice.total_amount_payable()}')
#     y_position -= 0.25 * inch
#     p.drawString(1 * inch, y_position, f'Total Amount Paid: {invoice.total_amount_paid()}')

#     # Add Payment History
#     y_position -= 0.5 * inch
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y_position, 'Payment History')
#     p.setFont("Helvetica", 12)
#     y_position -= 0.5 * inch

#     for i, receipt in enumerate(receipts, start=1):
#         p.drawString(1 * inch, y_position, f'{i}. Amount Paid: {receipt.amount_paid} - Date Paid: {receipt.date_paid.strftime("%Y-%m-%d")} - Comment: {receipt.comment}')
#         y_position -= 0.25 * inch

#     # Finish up the PDF
#     p.showPage()
#     p.save()
#     return response


# ###### another method:  working properly good downloaded the pdf format:
###......................###

# from django.shortcuts import get_object_or_404, HttpResponse
# from .models import Invoice, InvoiceItem, Receipt
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch  # Add this import
# from io import BytesIO

# def download_invoice(request, invoice_id):
#     # Fetch invoice details
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     items = InvoiceItem.objects.filter(invoice=invoice)
#     receipts = Receipt.objects.filter(invoice=invoice)

#     # Create a new PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
#     styles = getSampleStyleSheet()

#     # Header
#     p.setFont("Helvetica-Bold", 20)
#     p.drawString(1 * inch, height - 1 * inch, f'Invoice #{invoice.id}')

#     # Add invoice details
#     p.setFont("Helvetica", 12)
#     y = height - 1.5 * inch
#     p.drawString(1 * inch, y, f'Student Name: {invoice.student}')
#     y -= 0.25 * inch
#     p.drawString(1 * inch, y, f'Session: {invoice.session}')
#     y -= 0.25 * inch
#     p.drawString(1 * inch, y, f'Term: {invoice.term}')
#     y -= 0.25 * inch
#     p.drawString(1 * inch, y, f'Class: {invoice.class_for}')
#     y -= 0.25 * inch
#     p.drawString(1 * inch, y, f'Status: {invoice.get_status_display()}')
#     y -= 0.25 * inch
#     p.drawString(1 * inch, y, f'Expected Balance: {invoice.balance()}')

#     # Invoice Breakdown Table
#     y -= 0.5 * inch
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Invoice Breakdown')
#     y -= 0.25 * inch

#     data = [['S/N', 'Description', 'Amount']]
#     for i, item in enumerate(items, start=1):
#         data.append([i, item.description, item.amount])
#     data.append(['', 'Total Amount this term', invoice.amount_payable()])
#     data.append(['', 'Balance from previous term', invoice.balance_from_previous_term])
#     data.append(['', 'Total Amount Payable', invoice.total_amount_payable()])
#     data.append(['', 'Total Amount Paid', invoice.total_amount_paid()])

#     table = Table(data, colWidths=[0.5 * inch, 4 * inch, 1.5 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Adjust y position for the next section
#     y -= (len(data) * 0.25 * inch) + 0.75 * inch

#     # Payment History Table
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Payment History')
#     y -= 0.25 * inch

#     data = [['S/N', 'Amount Paid', 'Date Paid', 'Comment Paid']]
#     for i, receipt in enumerate(receipts, start=1):
#         data.append([i, receipt.amount_paid, receipt.date_paid.strftime('%Y-%m-%d'), receipt.comment])

#     table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.5 * inch, 3 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Finish up the PDF
#     p.showPage()
#     p.save()

#     pdf = buffer.getvalue()
#     buffer.close()
#     response.write(pdf)
#     return response


######### ######### ############ working good but,school sampleimage, and address all visible in single line issue:;;:

# from django.shortcuts import get_object_or_404, HttpResponse
# from .models import Invoice, InvoiceItem, Receipt
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch  # Add this import
# from io import BytesIO
# from django.conf import settings
# import os

# def download_invoice(request, invoice_id):
#     # Fetch invoice details
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     items = InvoiceItem.objects.filter(invoice=invoice)
#     receipts = Receipt.objects.filter(invoice=invoice)

#     # Create a new PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
#     styles = getSampleStyleSheet()


# # School Logo
#     logo_path = os.path.join(settings.STATIC_ROOT, 'dist/img/avatar.png')
#     p.drawImage(logo_path, 1 * inch, height - 1 * inch, width=50, height=50)

#     # School Address
#     school_address = """
#     Sample School Address:
#     6020 S Langley Avenue
#     Chicago, IL 60637
#     Phone: (773) 535-0990
#     Fax: (773) 535-0580
#     """
#     p.setFont("Helvetica", 10)
#     p.drawString(width - 300, height - 0.75 * inch, school_address)



#     # Header
#     p.setFont("Helvetica-Bold", 20)
#     p.drawString(1 * inch, height - 1 * inch, f'Invoice #{invoice.id}')

#     # Add invoice details and image
#     p.setFont("Helvetica", 12)
#     y = height - 1.5 * inch

#     if invoice.student.passport:
#         image_path = os.path.join(settings.MEDIA_ROOT, invoice.student.passport.name)
#     else:
#         image_path = os.path.join(settings.STATIC_ROOT, 'dist/img/avatar.png')

#     p.drawImage(image_path, 1 * inch, y - 1 * inch, width=1 * inch, height=1 * inch)

#     y -= 0.25 * inch
#     text_x = 2.5 * inch
#     p.drawString(text_x, y, f'Student Name: {invoice.student}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Session: {invoice.session}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Term: {invoice.term}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Class: {invoice.class_for}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Status: {invoice.get_status_display()}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Expected Balance: {invoice.balance()}')

#     # Invoice Breakdown Table
#     y -= 0.5 * inch
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Invoice Breakdown')
#     y -= 0.25 * inch

#     data = [['S/N', 'Description', 'Amount']]
#     for i, item in enumerate(items, start=1):
#         data.append([i, item.description, item.amount])
#     data.append(['', 'Total Amount this term', invoice.amount_payable()])
#     data.append(['', 'Balance from previous term', invoice.balance_from_previous_term])
#     data.append(['', 'Total Amount Payable', invoice.total_amount_payable()])
#     data.append(['', 'Total Amount Paid', invoice.total_amount_paid()])

#     table = Table(data, colWidths=[0.5 * inch, 4 * inch, 1.5 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Adjust y position for the next section
#     y -= (len(data) * 0.25 * inch) + 0.75 * inch

#     # Payment History Table
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Payment History')
#     y -= 0.25 * inch

#     data = [['S/N', 'Amount Paid', 'Date Paid', 'Comment Paid']]
#     for i, receipt in enumerate(receipts, start=1):
#         data.append([i, receipt.amount_paid, receipt.date_paid.strftime('%Y-%m-%d'), receipt.comment])

#     table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.5 * inch, 3 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Finish up the PDF
#     p.showPage()
#     p.save()

#     pdf = buffer.getvalue()
#     buffer.close()
#     response.write(pdf)
#     return response






############### 3.34pm text red color ah visible agum....


# from django.shortcuts import get_object_or_404, HttpResponse
# from .models import Invoice, InvoiceItem, Receipt
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch
# from io import BytesIO
# from django.conf import settings
# import os
# import random

# def generate_unique_invoice_number():
#     return f"{random.randint(100000, 999999)}"

# def download_invoice(request, invoice_id):
#     # Fetch invoice details
#     invoice = get_object_or_404(Invoice, pk=invoice_id)
#     items = InvoiceItem.objects.filter(invoice=invoice)
#     receipts = Receipt.objects.filter(invoice=invoice)

#     # Generate a unique invoice number
#     invoice_number = generate_unique_invoice_number()

#     # Create a new PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename=invoice_{invoice_number}.pdf'

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
#     styles = getSampleStyleSheet()

#     # Add school logo to the top left
#     logo_path = os.path.join(settings.STATIC_ROOT, 'dist/img/avatar.png')
#     p.drawImage(logo_path, 0.5 * inch, height - 1.5 * inch, width=1 * inch, height=1 * inch)

#     # Add school address to the top left
#     p.setFont("Helvetica", 10)
#     address_y = height - 1 * inch
#     p.drawString(1.75 * inch, address_y, "VERMANS INTERNATIONAL SCHOOL")
#     address_y -= 0.15 * inch
#     p.drawString(1.75 * inch, address_y, "452 Wilshire Blvd, Los Angeles, CA 90010")
#     address_y -= 0.15 * inch
#     p.drawString(1.75 * inch, address_y, "222-555-7777")
#     address_y -= 0.15 * inch
#     p.drawString(1.75 * inch, address_y, "inquiries@vermans.com")
#     address_y -= 0.15 * inch
#     p.drawString(1.75 * inch, address_y, "www.vermans.com")

#     # Add Invoice label
#     p.setFont("Helvetica-Bold", 20)
#     p.setFillColor(colors.red)
#     p.drawString(1 * inch, height - 2 * inch, "INVOICE")

#     # Add invoice details to the top right
#     p.setFont("Helvetica", 12)
#     details_y = height - 1 * inch
#     details_x = width - 2.5 * inch
#     p.drawString(details_x, details_y, "Invoice Date: " + invoice.date.strftime('%B %d, %Y'))  # Replace 'date' with the appropriate field
#     details_y -= 0.25 * inch
#     p.drawString(details_x, details_y, f"Invoice No.: {invoice_number}")

#     # Add invoice details and image
#     y = height - 3 * inch

#     if invoice.student.passport:
#         image_path = os.path.join(settings.MEDIA_ROOT, invoice.student.passport.name)
#     else:
#         image_path = os.path.join(settings.STATIC_ROOT, 'dist/img/avatar.png')

#     p.drawImage(image_path, 1 * inch, y - 1 * inch, width=1 * inch, height=1 * inch)

#     y -= 0.25 * inch
#     text_x = 2.5 * inch
#     p.drawString(text_x, y, f'Student Name: {invoice.student}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Session: {invoice.session}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Term: {invoice.term}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Class: {invoice.class_for}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Status: {invoice.get_status_display()}')
#     y -= 0.25 * inch
#     p.drawString(text_x, y, f'Expected Balance: {invoice.balance()}')

#     # Invoice Breakdown Table
#     y -= 0.5 * inch
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Invoice Breakdown')
#     y -= 0.25 * inch

#     data = [['S/N', 'Description', 'Amount']]
#     for i, item in enumerate(items, start=1):
#         data.append([i, item.description, item.amount])
#     data.append(['', 'Total Amount this term', invoice.amount_payable()])
#     data.append(['', 'Balance from previous term', invoice.balance_from_previous_term])
#     data.append(['', 'Total Amount Payable', invoice.total_amount_payable()])
#     data.append(['', 'Total Amount Paid', invoice.total_amount_paid()])

#     table = Table(data, colWidths=[0.5 * inch, 4 * inch, 1.5 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Adjust y position for the next section
#     y -= (len(data) * 0.25 * inch) + 0.75 * inch

#     # Payment History Table
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(1 * inch, y, 'Payment History')
#     y -= 0.25 * inch

#     data = [['S/N', 'Amount Paid', 'Date Paid', 'Comment Paid']]
#     for i, receipt in enumerate(receipts, start=1):
#         data.append([i, receipt.amount_paid, receipt.date_paid.strftime('%Y-%m-%d'), receipt.comment])

#     table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.5 * inch, 3 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     table.wrapOn(p, width, height)
#     table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

#     # Finish up the PDF
#     p.showPage()
#     p.save()

#     pdf = buffer.getvalue()
#     buffer.close()
#     response.write(pdf)
#     return response



# ##########################

from django.shortcuts import get_object_or_404, HttpResponse
from .models import Invoice, InvoiceItem, Receipt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from django.conf import settings
import os
import random

def generate_unique_invoice_number():
    return f"{random.randint(100000, 999999)}"

def download_invoice(request, invoice_id):
    # Fetch invoice details
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    receipts = Receipt.objects.filter(invoice=invoice)

    # Generate a unique invoice number
    invoice_number = generate_unique_invoice_number()

    # Create a new PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice_number}.pdf'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()

    # Add school logo to the top left
    logo_path = os.path.join(settings.STATIC_ROOT, 'dist/img/school.png')
    # logo_path = os.path.join(settings.STATIC_ROOT, 'C:\Users\prasa\OneDrive\Documents\Django-sms-git\Django-SMS\static\dist\img\school7.png')
    p.drawImage(logo_path, 0.5 * inch, height - 1.5 * inch, width=1 * inch, height=1 * inch)

    # Add school address to the top left
    p.setFont("Helvetica", 10)
    address_y = height - 1 * inch
    p.drawString(1.75 * inch, address_y, "VERMANS INTERNATIONAL SCHOOL")
    address_y -= 0.15 * inch
    p.drawString(1.75 * inch, address_y, "452 Wilshire Blvd, Los Angeles, CA 90010")
    address_y -= 0.15 * inch
    p.drawString(1.75 * inch, address_y, "222-555-7777")
    address_y -= 0.15 * inch
    p.drawString(1.75 * inch, address_y, "inquiries@vermans.com")
    address_y -= 0.15 * inch
    p.drawString(1.75 * inch, address_y, "www.vermans.com")

    # Add invoice details to the top right
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    details_y = height - 0.9 * inch
    details_x = width - 2.5 * inch
    p.drawString(details_x, details_y, "Invoice Date: " + invoice.date.strftime('%B %d, %Y'))  # Replace 'date' with the appropriate field
    details_y -= 0.25 * inch
    p.drawString(details_x, details_y, f"Invoice No.: {invoice_number}")

    # Add Invoice label
    # p.setFont("Helvetica-Bold", 20)
    # p.setFillColor(colors.red)
    # p.drawString(1 * inch, height - 2 * inch, "INVOICE123")

    # Section: Student details on the left, student image on the right
    y = height - 3 * inch
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    text_x = 1 * inch

    p.drawString(text_x, y, f'Student Name: {invoice.student}')
    y -= 0.25 * inch
    p.drawString(text_x, y, f'Session: {invoice.session}')
    y -= 0.25 * inch
    p.drawString(text_x, y, f'Term: {invoice.term}')
    y -= 0.25 * inch
    p.drawString(text_x, y, f'Class: {invoice.class_for}')
    y -= 0.25 * inch
    p.drawString(text_x, y, f'Status: {invoice.get_status_display()}')
    y -= 0.25 * inch
    p.drawString(text_x, y, f'Expected Balance: {invoice.balance()}')

    # Student image on the right
    image_y = height - 3 * inch
    image_path = os.path.join(settings.MEDIA_ROOT, invoice.student.passport.name) if invoice.student.passport else os.path.join(settings.STATIC_ROOT, 'dist/img/avatar.png')
    p.drawImage(image_path, width - 2.5 * inch, image_y - 1 * inch, width=1 * inch, height=1 * inch)

    # Invoice Breakdown Table
    y -= 0.5 * inch
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y, 'Invoice Breakdown')
    y -= 0.25 * inch

    data = [['S/N', 'Description', 'Amount']]
    for i, item in enumerate(items, start=1):
        data.append([i, item.description, item.amount])
    data.append(['', 'Total Amount this term', invoice.amount_payable()])
    data.append(['', 'Balance from previous term', invoice.balance_from_previous_term])
    data.append(['', 'Total Amount Payable', invoice.total_amount_payable()])
    data.append(['', 'Total Amount Paid', invoice.total_amount_paid()])

    table = Table(data, colWidths=[0.5 * inch, 4 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

    # Adjust y position for the next section
    y -= (len(data) * 0.25 * inch) + 0.75 * inch

    # Payment History Table
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, y, 'Payment History')
    y -= 0.25 * inch

    data = [['S/N', 'Amount Paid', 'Date Paid', 'Comment Paid']]
    for i, receipt in enumerate(receipts, start=1):
        data.append([i, receipt.amount_paid, receipt.date_paid.strftime('%Y-%m-%d'), receipt.comment])

    table = Table(data, colWidths=[0.5 * inch, 1.5 * inch, 1.5 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 1 * inch, y - (len(data) * 0.25 * inch))

    # Finish up the PDF
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response





#......................................










### ### ###

# from django.shortcuts import render, redirect
# from .forms import StudentForm

# def student_create(request):
#     if request.method == 'POST':
#         form = StudentForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('student_list')
#     else:
#         form = StudentForm()
#     return render(request, 'student_form.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from .models import Student

def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'student_detail.html', {'object': student})

