from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import logging

# Create a Flask Application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

# Create a Database Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flatmate_name = db.Column(db.String(50), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Define exchange rates (CZK is the base currency)
exchangeRates = {
    'CZK': 1,
    'USD': None,
    'EUR': None,
    'GBP': None
}

def fetch_exchange_rates():
    try:
        api_url = "https://data-api.ecb.europa.eu/service/data/EXR/D.CZK.EUR.SP00.A?lastNObservations=1&format=jsondata"
        response = requests.get(api_url)
        data = response.json()
        
        # Extract the exchange rate value from the JSON data
        exchange_rate = data['dataSets'][0]['series']['0:0:0:0:0']['observations']['0'][0]
        
        # Update the exchangeRates dictionary
        exchangeRates['EUR'] = 1/exchange_rate

    except Exception as e:
        print("Error fetching exchange rates:", str(e))

fetch_exchange_rates()

def convert_czk_to_eur(amount_in_czk):
    if exchangeRates['EUR'] is not None:
        return amount_in_czk / exchangeRates['EUR']
    else:
        return None  # Handle the case where the exchange rate is not available


# Calculate total expenses
def calculate_total_expenses():
    total_expenses = sum(expense.cost for expense in Expense.query.all())
    return total_expenses

def calculate_owed_amounts(total_expenses):
    # Retrieve unique flatmates
    flatmates = db.session.query(Expense.flatmate_name).distinct().all()

    # Calculate the total amount paid by each flatmate for each item
    total_amount_paid = {}
    try:
        for flatmate in flatmates:
            flatmate_name = flatmate[0]
            total_amount_paid[flatmate_name] = 0  # Initialize to 0
            expenses_for_flatmate = Expense.query.filter_by(flatmate_name=flatmate_name).all()
            for expense in expenses_for_flatmate:
                total_amount_paid[flatmate_name] += expense.cost

        # Calculate the average amount to be paid by each flatmate
        num_flatmates = len(flatmates)
        average_amount = total_expenses / num_flatmates

        # Calculate owed amounts for each flatmate
        owed_amounts = {}
        for flatmate in flatmates:
            flatmate_name = flatmate[0]
            amount_paid = total_amount_paid[flatmate_name]
            owed_amount = amount_paid - average_amount
            owed_amounts[flatmate_name] = round(owed_amount, 2)  # Round to two decimal places
    except Exception as e:
        print("Error calculating owed amounts:", str(e))
        owed_amounts = {}  # Return an empty dictionary in case of an error

    return owed_amounts

# Create routes
@app.route('/')
def index():
    total_expenses = calculate_total_expenses()
    owed_amounts = calculate_owed_amounts(total_expenses)  # Calculate owed amounts
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses, owed_amounts=owed_amounts, exchangeRates=exchangeRates)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        flatmate_name = request.form.get('flatmate_name')
        item = request.form.get('item')
        cost = float(request.form.get('cost'))

        expense = Expense(flatmate_name=flatmate_name, item=item, cost=cost)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_expense.html')  # Display the form for adding expenses

# Run the application
'''
if __name__ == '__main__':
    # Fetch exchange rates when the app starts
    app.run(debug=True)
'''