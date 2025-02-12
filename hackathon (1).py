from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import sqlite3


driver = webdriver.Chrome()

driver.get('https://messages.google.com/web')
print("Scan the QR code with your phone to log in.")
time.sleep(30)


messages = driver.find_elements(By.CSS_SELECTOR, '.ng-star-inserted')

with open("messages.txt", "a", encoding="utf-8") as file:  # Changed "w" to "a"
    for message in messages:
        text = message.text.strip()
        if text:
            file.write(text + "\n")

print("All messages have been appended to 'messages.txt'.")

# Step 4: Close the browser
driver.quit()

# Step 5: Connect to SQLite database
conn = sqlite3.connect('budget_tracker.db')
cursor = conn.cursor()

# Create table for transactions if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT
)
''')
conn.commit()

# Step 6: Parse and prompt user to categorize transactions from the messages file
with open("messages.txt", "r", encoding="utf-8") as file:
    for line in file:
        # Check for keywords and amounts
        if 'debited' in line.lower():
            match = re.search(r'debited by\s*([\d,]+(?:\.\d{1,2})?)', line, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))  # Convert to float, removing any commas
                print(f"\nTransaction found: Expense of ₹{amount:.2f}")
                category = input("Enter a category for this expense (e.g., Food, Transport, Entertainment): ")
                cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                               ("Expense", amount, category))
                conn.commit()

        elif 'credited' in line.lower():
            match = re.search(r'credited by\s*([\d,]+(?:\.\d{1,2})?)', line, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))  # Convert to float, removing any commas
                print(f"\nTransaction found: Income of ₹{amount:.2f}")
                category = input("Enter a category for this income (e.g., Salary, Refund, Gift): ")
                cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                               ("Income", amount, category))
                conn.commit()

print("All transactions have been processed and added to the database.")

# Close the database connection
cursor.execute('''
select * from transactions;
''')
conn.commit()
conn.close()