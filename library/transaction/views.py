from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transaction.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID,BorrowBook
from datetime import datetime
from django.db.models import Sum
from transaction.forms import (
    DepositForm,
    WithdrawForm,
    LoanRequestForm,
)
from book.models import Book,Profile
from django.http import JsonResponse
from django.views import View
from .forms import PurchaseForm
from .models import Transaction
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')
 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        
        account.balance += amount 
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        ) 
        send_transaction_email(self.request.user, amount, "Deposit Message", "transaction/deposit_email.html")

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
    
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        send_transaction_email(self.request.user, amount, "Withdrawal Message", "transaction/withdraw_email.html")

        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction/transaction_report.html'
    model = Transaction
    balance = 0 
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context
    


# def buy_now(request, book_id):
#     book = Book.objects.get(id=book_id)
#     user_profile, created = Profile.objects.get_or_create(user=request.user)

#     # Check if the user has enough balance to buy the book
#     if request.user.account.balance >= book.borrowing_price:
#         # Create a transaction for the purchase
#         transaction = Transaction.objects.create(
#             account=request.user.account,
#             amount=book.borrowing_price,
#             transaction_type=BorrowBook,
#         )

#         # Update user's account balance
#         request.user.account.balance -= book.borrowing_price
#         request.user.account.save(update_fields=['balance'])

#         # Add the book to the user's saved books
#         user_profile.saved_books.add(book)

#         messages.success(
#             request,
#             f'Successfully purchased the book: {book.title}. Amount {"{:,.2f}".format(float(book.borrowing_price))}$ was withdrawn from your account.'
#         )
        
#     else:
#         messages.error(
#             request,
#             f'Insufficient balance to purchase the book: {book.title}.'
#         )

#     return redirect('profile')


def buy_now(request, book_id):
    book = Book.objects.get(id=book_id)
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.account.balance >= book.borrowing_price:
       
        transaction = Transaction.objects.create(
            account=request.user.account,
            amount=book.borrowing_price,
            transaction_type=BorrowBook,
        )

        # Update user's account balance
        request.user.account.balance -= book.borrowing_price
        request.user.account.save(update_fields=['balance'])

     
        user_profile.saved_books.add(book)

        subject = "Book Purchase Confirmation"
        template = "transaction/borrowbook_email.html"
        send_transaction_email(request.user, book.borrowing_price, subject, template)

        messages.success(
            request,
            f'Successfully purchased the book: {book.title}. Amount {"{:,.2f}".format(float(book.borrowing_price))}$ was withdrawn from your account.'
        )
    else:
        messages.error(
            request,
            f'Insufficient balance to purchase the book: {book.title}.'
        )

    return redirect('profile')