from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


#Create a Flask Application:
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)


#Create a Database Model:
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flatmate_name = db.Column(db.String(50), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)

#Initialize the database
with app.app_context():
    db.create_all()



#Create routes:
@app.route('/')
def index():
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses)

@app.route('/add_expense', methods=['GET','POST'])
def add_expense():
    flatmate_name = request.form.get('flatmate_name')
    item = request.form.get('item')
    cost = float(request.form.get('cost'))

    expense = Expense(flatmate_name=flatmate_name, item=item, cost=cost)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for('index'))

#Create templates - create 'templates' directory and 
# add there HTML files with the templates for the application views

#Run application:
if __name__ == '__main__':
    app.run(debug=True)
