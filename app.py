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

# Create routes
@app.route('/')
def index():
    expenses = Expense.query.all()
    owed_amounts = calculate_owed_amounts()  # Calculate owed amounts
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

# Calculate Owed Amounts
def calculate_owed_amounts():
    # Retrieve expenses for each flatmate
    flatmates = db.session.query(Expense.flatmate_name).distinct().all()

    # Calculate owed amounts for each flatmate
    owed_amounts = {}
    for flatmate in flatmates:
        flatmate_name = flatmate[0]
        total_expenses = sum(expense.cost for expense in Expense.query.filter_by(flatmate_name=flatmate_name).all())
        total_share = total_expenses / len(flatmates)
        owed_amount = total_share - total_expenses
        owed_amounts[flatmate_name] = owed_amount

    return owed_amounts

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
