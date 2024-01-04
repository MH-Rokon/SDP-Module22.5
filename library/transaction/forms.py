from django import forms
from .models import Transaction
from accounts.models import UserBookAccount
from book.models import Book
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 100
        balance = account.balance 
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can borrow at least {min_withdraw_amount} $'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not buy more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        min_loan_amount = 1000  
        amount = self.cleaned_data.get('amount')

        if amount < min_loan_amount:
            raise forms.ValidationError(
                f'You need to request at least {min_loan_amount} $'
            )

        return amount

# transaction/forms.py
from django import forms

class PurchaseForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())
    amount = forms.DecimalField(min_value=0.01, widget=forms.HiddenInput())
