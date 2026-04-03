from flask import Flask, render_template, request, redirect, session
from models import db, User, Food, Order
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def home():
    foods = Food.query.all()
    return render_template('index.html', foods=foods)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(id)
    session.modified = True
    return redirect('/cart')

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    items = Food.query.filter(Food.id.in_(session['cart'])).all()
    return render_template('cart.html', items=items)

@app.route('/order')
def order():
    if 'user_id' not in session:
        return redirect('/login')

    items = Food.query.filter(Food.id.in_(session['cart'])).all()
    for item in items:
        order = Order(user_id=session['user_id'], food_name=item.name)
        db.session.add(order)

    db.session.commit()
    session['cart'] = []
    return "Order Placed!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
