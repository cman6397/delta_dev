# delta_dev

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

