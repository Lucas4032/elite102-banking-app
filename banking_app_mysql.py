import mysql.connector
from mysql.connector import Error

#This is all my configuration i used to connect to mysql i also imported it in lines 1 and 2
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "#Lucasmowers1",
    "database": "banking_db"
}

#the database connection
def get_connection():
    """Return a MySQL connection using DB_CONFIG."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"  Database connection error: {e}")
        print("      Check your DB_CONFIG settings at the top of this file.")
        return None


def setup_database():
    """Create tables if they don't already exist."""
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id         INT           AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100)  NOT NULL,
            balance    DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id         INT           AUTO_INCREMENT PRIMARY KEY,
            account_id INT           NOT NULL,
            type       VARCHAR(20)   NOT NULL,
            amount     DECIMAL(15,2) NOT NULL,
            timestamp  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


#my banking functions
def create_account(name: str, initial_deposit: float) -> None:
    if initial_deposit < 0:
        print("   Initial deposit cannot be negative.")
        return

    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO accounts (name, balance) VALUES (%s, %s)",
        (name, initial_deposit)
    )
    account_id = cursor.lastrowid

    if initial_deposit > 0:
        cursor.execute(
            "INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'deposit', %s)",
            (account_id, initial_deposit)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n   Account created!")
    print(f"      Account ID : {account_id}")
    print(f"      Name       : {name}")
    print(f"      Balance    : ${initial_deposit:,.2f}")


def deposit(account_id: int, amount: float) -> None:
    if amount <= 0:
        print("   Deposit amount must be positive.")
        return

    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
    account = cursor.fetchone()

    if not account:
        print(f"   No account found with ID {account_id}.")
        cursor.close()
        conn.close()
        return

    new_balance = float(account["balance"]) + amount
    cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account_id))
    cursor.execute(
        "INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'deposit', %s)",
        (account_id, amount)
    )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n    Deposit successful!")
    print(f"      Deposited  : ${amount:,.2f}")
    print(f"      New balance: ${new_balance:,.2f}")


def withdraw(account_id: int, amount: float) -> None:
    if amount <= 0:
        print("   Withdrawal amount must be positive.")
        return

    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
    account = cursor.fetchone()

    if not account:
        print(f"   No account found with ID {account_id}.")
        cursor.close()
        conn.close()
        return

    current_balance = float(account["balance"])
    if current_balance < amount:
        print(f"   Insufficient funds.")
        print(f"      Current balance : ${current_balance:,.2f}")
        print(f"      Requested       : ${amount:,.2f}")
        cursor.close()
        conn.close()
        return

    new_balance = current_balance - amount
    cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account_id))
    cursor.execute(
        "INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'withdrawal', %s)",
        (account_id, amount)
    )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n   Withdrawal successful!")
    print(f"      Withdrawn  : ${amount:,.2f}")
    print(f"      New balance: ${new_balance:,.2f}")


def check_balance(account_id: int) -> None:
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    conn.close()

    if not account:
        print(f"   No account found with ID {account_id}.")
        return

    print(f"\n  --- Account Info ---")
    print(f"  ID      : {account['id']}")
    print(f"  Name    : {account['name']}")
    print(f"  Balance : ${float(account['balance']):,.2f}")
    print(f"  Opened  : {account['created_at']}")


def list_accounts() -> None:
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts ORDER BY id")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()

    if not accounts:
        print("\n  No accounts found. Create one first!")
        return

    print(f"\n  {'ID':<6} {'Name':<22} {'Balance':<14} {'Created'}")
    print("  " + "-" * 58)
    for acc in accounts:
        print(f"  {acc['id']:<6} {acc['name']:<22} ${float(acc['balance']):<13,.2f} {acc['created_at']}")


def view_transactions(account_id: int) -> None:
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM accounts WHERE id = %s", (account_id,))
    account = cursor.fetchone()

    if not account:
        print(f"   No account found with ID {account_id}.")
        cursor.close()
        conn.close()
        return

    cursor.execute(
        "SELECT * FROM transactions WHERE account_id = %s ORDER BY timestamp DESC",
        (account_id,)
    )
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"\n  --- Transactions for {account['name']} (ID {account_id}) ---")
    if not transactions:
        print("  No transactions yet.")
        return

    print(f"  {'#':<6} {'Type':<14} {'Amount':<14} {'Timestamp'}")
    print("  " + "-" * 52)
    for t in transactions:
        print(f"  {t['id']:<6} {t['type']:<14} ${float(t['amount']):<13,.2f} {t['timestamp']}")



def prompt_account_id(prompt: str = "  Enter account ID: ") -> int | None:
    try:
        return int(input(prompt))
    except ValueError:
        print("   Please enter a valid number.")
        return None


def prompt_amount(prompt: str = "  Enter amount: $") -> float | None:
    try:
        value = float(input(prompt))
        if value <= 0:
            print("  Amount must be greater than $0.")
            return None
        return value
    except ValueError:
        print("   Please enter a valid number.")
        return None

#everything below is my menu ui basically
def print_menu() -> None:
    print("" + "=" * 44)
    print("        MOWERS BANKING SYSTEM  ")
    print("=" * 44)
    print("  1.  Create New Account")
    print("  2.  Deposit Money")
    print("  3.  Withdraw Money")
    print("  4.  Check Balance")
    print("  5.  List All Accounts")
    print("  6.  View Transaction History")
    print("  0.  Exit")
    print("=" * 44)


def main() -> None:
    setup_database()
    print("Welcome to the Mowers Banking System!")
    print("Connected to MySQL database: banking_db")

    while True:
        print_menu()
        choice = input("  Select an option: ").strip()

        if choice == "1":
            name = input("  Account holder name: ").strip()
            if not name:
                print("   Name cannot be empty.")
                continue
            raw = input("  Initial deposit (press Enter for $0): $").strip()
            initial = float(raw) if raw else 0.0
            create_account(name, initial)

        elif choice == "2":
            acct_id = prompt_account_id()
            if acct_id is None:
                continue
            amount = prompt_amount()
            if amount:
                deposit(acct_id, amount)

        elif choice == "3":
            acct_id = prompt_account_id()
            if acct_id is None:
                continue
            amount = prompt_amount()
            if amount:
                withdraw(acct_id, amount)

        elif choice == "4":
            acct_id = prompt_account_id()
            if acct_id:
                check_balance(acct_id)

        elif choice == "5":
            list_accounts()

        elif choice == "6":
            acct_id = prompt_account_id()
            if acct_id:
                view_transactions(acct_id)

        elif choice == "0":
            print("Thanks for choosing the Mowers Banking app and I hope to see you soon! Goodbye.")
            break

        else:
            print("Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main()
