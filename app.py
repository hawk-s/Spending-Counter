from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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

# Calculate total expenses
def calculate_total_expenses():
    total_expenses = sum(expense.cost for expense in Expense.query.all())
    return total_expenses

# Calculate Owed Amounts
def calculate_owed_amounts(total_expenses):
    # Retrieve unique flatmates
    flatmates = db.session.query(Expense.flatmate_name).distinct().all()

    # Calculate the total amount paid by each flatmate for each item
    total_amount_paid = {}
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

    return owed_amounts


# Create routes
@app.route('/')
def index():
    total_expenses = calculate_total_expenses()
    owed_amounts = calculate_owed_amounts(total_expenses)  # Calculate owed amounts
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses, owed_amounts=owed_amounts)

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
if __name__ == '__main__':
    app.run(debug=True)
