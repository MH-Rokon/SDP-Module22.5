from django.urls import path
from .views import DepositMoneyView, WithdrawMoneyView, TransactionReportView,BorrowBook
from . import views

# app_name = 'transactions'
urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    # path("loans/<int:loan_id>/", PayLoanView.as_view(), name="pay"),
    path('buy_now/<int:book_id>/', views.buy_now, name='buy_now'),
]

#   path("withdraw_books/", WithdrawBookView.as_view(), name="withdraw_books"),
#   path("books/", bookView.as_view(), name="books"),