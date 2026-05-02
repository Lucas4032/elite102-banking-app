# Elite 102 / Mowers Banking App
------------------------------------
This is a command line banking system that I built in MySQL and Python

#Setup Instructions
----------------------

Requirements
---------------
- Python 3.x
- MySQL Server
- mysql-connector-python

Installation
--------------
1. Clone the repository
   git clone https://github.com/Lucas4032/elite102-banking-app.git  (<- command to clone)

2. Then install the Python connector
   pip install mysql-connector-python (<- command to install)

3. Then you have to set up the database
   - Open MySQL Workbench
   - Run setup_mysql.sql to create the database and tables

4. Configure based on your own MySQL password
- Open banking_app_mysql.py
- Change line 8 to your MySQL root password
  
6. Last but not least, run the app
- python banking_app_mysql.py
  
#Features
--------------
- Can create bank accounts
- Deposit and withdraw money
- Check account balance
- List all accounts
- View transaction history
