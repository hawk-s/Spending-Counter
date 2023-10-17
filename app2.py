from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Create a Flask Application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

# Database Models
class Flatmate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    expenses = db.relationship('Expense', backref='flatmate', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flatmate_id = db.Column(db.Integer, db.ForeignKey('flatmate.id'), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)

# Calculate Owed Amounts
def calculate_owed_amounts():
    # Retrieve expenses for each flatmate
    flatmates = Flatmate.query.all()
    
    # Calculate owed amounts for each flatmate
    owed_amounts = {}
    for flatmate in flatmates:
        total_expenses = sum(expense.cost for expense in flatmate.expenses)
        total_share = total_expenses / len(flatmates)
        owed_amount = total_share - total_expenses
        owed_amounts[flatmate.name] = owed_amount

    return owed_amounts

# Routes and Templates
@app.route('/')
def index():
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        flatmate_name = request.form.get('flatmate_name')
        item = request.form.get('item')
        cost = float(request.form.get('cost'))

        # Get flatmate by name (you may want to implement a lookup function)
        flatmate = Flatmate.query.filter_by(name=flatmate_name).first()

        if flatmate:
            expense = Expense(flatmate_id=flatmate.id, item=item, cost=cost)
            db.session.add(expense)
            db.session.commit()
            return redirect(url_for('index'))

    flatmates = Flatmate.query.all()
    return render_template('add_expense.html', flatmates=flatmates)

@app.route('/owed_amounts')
def display_owed_amounts():
    owed_amounts = calculate_owed_amounts()
    return render_template('owed_amounts.html', owed_amounts=owed_amounts)

if __name__ == '__main__':
    app.run(debug=True)
