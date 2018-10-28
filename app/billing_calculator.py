from app import app
from app import db
from app.forms import LoginForm, Fee_StructureForm, Billing_GroupForm, SplitForm, Account_DetailsForm, Add_AccountForm, Remove_AccountForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure, Split, Account_Split, Account_History, Account_Fee
import datetime,decimal

class billing_calculator:
    def __init__(self, quarterly_data, monthly_data):
        self.quarterly_data = quarterly_data
        self.monthly_data = monthly_data

    def run_billing(self):
        Account_Fee.query.delete()
        db.session.commit()

        count = 0
        for quarterly_row in self.quarterly_data:
            monthly_row = self.monthly_data[count]
            self.calculate_row(quarterly_row, monthly_row)
            count+=1

        db.session.commit()

    def calculate_row(self, quarterly_row, monthly_row):
        row = quarterly_row
        fee_structure = row[1]

        if fee_structure.frequency == 'monthly':
            row = monthly_row

        account = row[0]
        average_balance = row.Average_Balance
        billing_balance = account.balance
        fee = fee_structure.flat_fee

        account_fee = Account_Fee()
        fee_portion = 0.25

        if fee_structure.frequency == 'monthly':
            fee_portion = 1/12
     
        if fee_structure.valuation_method == 'Average Daily Balance':
            billing_balance = average_balance

        if fee_structure.structure == 'Flat Rate':
            flat_rate = fee_structure.flat_rate
            fee = float(flat_rate) * fee_portion * float(billing_balance)
        
        if account.fee_location:
            account_fee.account = account.fee_location
            account_fee.fee = fee
        else:
            account_fee.account = account
            account_fee.fee = fee

        db.session.add(account_fee)



