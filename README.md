# delta_dev

## Installation:
clone from github. Set up a virtual environment with python 3.x.  Install requirements in requirements.txt.  
Set Flask variable: (export FLASK_APP=delta_billing.py). Run fill_random.py.  Run tests.py. 
Start the application: flask run.

Login using username:admin, password:1234

##
The application was never finished.  This was a learning project intended to address a problem of someone close to me who is an investment advisor.  It was my first attempt at an application.

## Summary:
Delta_Dev is a web application designed for managing account billing for Investment Advisors.
The application is basically a UI on top of a relational database that allows Users to modify 
and maintain relationships between accounts and fees.  

## Account Groups:

#### Accounts: 
At the lowest level, accounts represent the individual brokerage accounts that are under management by the Investment advisor.
Each account has an owner, a balance, and a history of trades and positions.  

#### Households:
Households are the next level above accounts.  Households are collections of accounts with the same owner.  Households are constructed
automatically from account detail files provided by the brokerage.  In this case TD Ameritrade.

#### Billing Groups: 
Billing Groups are the next level of households although it is often close to a one to one relationship between the two.  Billing Groups are essentially customizable households where any accounts can be grouped together.  This feature allows the Investment advisor to create their own groups when household groupings are too narrow or confining.  

## Billing Structures:
#### Fee Structures:
Fee structures are created through the web application and mapped to Accounts to define billing rates, frequencies, cycles, collection types, valuation methods and more.  Fee structures can be quickly created, edited, or removed and can be assigned to one or multiple accounts at a time. 

#### Splits:
Splits are used to split the fees between different advisors post billing.  Splits are created and assigned in a similar fashion to fee structures.

#### Billing:
When Billing is run, the structures and information in the program are used to generate reports and fees at Account, Household, and Billing Group levels for use of the Investment Advisor.  

