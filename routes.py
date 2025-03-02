from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Restaurant, MenuItem, Order, OrderItem # Added OrderItem import
from forms import LoginForm, RegisterForm
import logging

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('restaurants'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('restaurants'))
        flash('Invalid email or password')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('restaurants'))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.')
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/restaurants')
@login_required
def restaurants():
    restaurants = Restaurant.query.all()
    return render_template('restaurants/list.html', restaurants=restaurants)

@app.route('/restaurant/<int:id>')
@login_required
def restaurant_menu(id):
    restaurant = Restaurant.query.get_or_404(id)
    menu_items = MenuItem.query.filter_by(restaurant_id=id).all()
    return render_template('restaurants/menu.html', 
                         restaurant=restaurant, 
                         menu_items=menu_items)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {})

    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += 1
    else:
        cart[str(item_id)] = {
            'name': item.name,
            'price': item.price,
            'quantity': 1,
            'restaurant_name': item.restaurant.name,
            'restaurant_id': item.restaurant_id
        }

    session['cart'] = cart
    flash(f'{item.name} added to cart!')
    return redirect(url_for('restaurant_menu', id=item.restaurant_id))

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_amount = 0

    for item_id, item_data in cart.items():
        item_total = item_data['price'] * item_data['quantity']
        cart_items.append({
            'id': item_id,
            'name': item_data['name'],
            'price': item_data['price'],
            'quantity': item_data['quantity'],
            'restaurant_name': item_data['restaurant_name'],
            'total': item_total
        })
        total_amount += item_total

    return render_template('cart/cart.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/update_cart/<item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart = session.get('cart', {})
    action = request.json.get('action')

    if str(item_id) in cart:
        if action == 'increase':
            cart[str(item_id)]['quantity'] += 1
        elif action == 'decrease':
            cart[str(item_id)]['quantity'] -= 1
            if cart[str(item_id)]['quantity'] <= 0:
                del cart[str(item_id)]

    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/remove_from_cart/<item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!')
        return redirect(url_for('view_cart'))

    try:
        # Group items by restaurant
        restaurant_orders = {}
        for item_id, item_data in cart.items():
            restaurant_id = item_data['restaurant_id']
            if restaurant_id not in restaurant_orders:
                restaurant_orders[restaurant_id] = {
                    'items': [],
                    'total': 0
                }
            item_total = item_data['price'] * item_data['quantity']
            restaurant_orders[restaurant_id]['items'].append({
                'menu_item_id': int(item_id),
                'quantity': item_data['quantity'],
                'price': item_data['price']
            })
            restaurant_orders[restaurant_id]['total'] += item_total

        # Create orders for each restaurant
        for restaurant_id, order_data in restaurant_orders.items():
            order = Order(
                user_id=current_user.id,
                restaurant_id=restaurant_id,
                total_amount=order_data['total']
            )
            db.session.add(order)
            db.session.flush()  # Get order ID

            # Create order items
            for item in order_data['items']:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item['menu_item_id'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_item)

        db.session.commit()
        session['cart'] = {}
        flash('Order placed successfully!')
        return redirect(url_for('order_history'))

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error placing order: {str(e)}")
        flash('Error placing order. Please try again.')
        return redirect(url_for('view_cart'))

# Initialize sample data
def init_sample_data():
    try:
        if Restaurant.query.first() is None:
            restaurants = [
                {
                    "name": "Faisal Mess",
                    "description": "Famous for traditional Pakistani cuisine",
                    "image_url": "https://source.unsplash.com/800x600/?pakistani-food"
                },
                {
                    "name": "Tariq Dhaba",
                    "description": "Best street food and chai",
                    "image_url": "https://source.unsplash.com/800x600/?street-food"
                },
                {
                    "name": "Kashif Chorahi",
                    "description": "Local specialties and fresh food",
                    "image_url": "https://source.unsplash.com/800x600/?local-food"
                },
                {
                    "name": "Girls Hostel Mess",
                    "description": "Healthy and homestyle cooking",
                    "image_url": "https://source.unsplash.com/800x600/?healthy-food"
                },
                {
                    "name": "Boys Hostel Mess",
                    "description": "Quick meals and student favorites",
                    "image_url": "https://source.unsplash.com/800x600/?fast-food"
                }
            ]

            # Create restaurants
            created_restaurants = {}
            for restaurant_data in restaurants:
                restaurant = Restaurant(**restaurant_data)
                db.session.add(restaurant)
                db.session.flush()  # Get ID before commit
                created_restaurants[restaurant.name] = restaurant.id

            # Define menu items for each restaurant
            menu_items = {
                "Faisal Mess": [
                    {
                        "name": "Chicken Biryani",
                        "description": "Aromatic rice dish with tender chicken and spices",
                        "price": 150.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?biryani"
                    },
                    {
                        "name": "Beef Karahi",
                        "description": "Spicy beef curry cooked in a traditional wok",
                        "price": 250.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?curry"
                    },
                    {
                        "name": "Kashmiri Chai",
                        "description": "Pink tea with nuts and cream",
                        "price": 50.00,
                        "category": "beverage",
                        "image_url": "https://source.unsplash.com/800x600/?pink-tea"
                    },
                    {
                        "name": "Lab-e-Shireen",
                        "description": "Traditional sweet dessert with milk and dates",
                        "price": 100.00,
                        "category": "dessert",
                        "image_url": "https://source.unsplash.com/800x600/?sweet-dessert"
                    }
                ],
                "Tariq Dhaba": [
                    {
                        "name": "Paratha Roll",
                        "description": "Flatbread wrapped with spicy meat filling",
                        "price": 120.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?wrap"
                    },
                    {
                        "name": "Doodh Patti",
                        "description": "Strong milk tea",
                        "price": 30.00,
                        "category": "beverage",
                        "image_url": "https://source.unsplash.com/800x600/?milk-tea"
                    },
                    {
                        "name": "Kheer",
                        "description": "Rice pudding with cardamom and nuts",
                        "price": 80.00,
                        "category": "dessert",
                        "image_url": "https://source.unsplash.com/800x600/?rice-pudding"
                    }
                ],
                "Kashif Chorahi": [
                    {
                        "name": "Nihari",
                        "description": "Slow-cooked beef stew with spices",
                        "price": 200.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?beef-stew"
                    },
                    {
                        "name": "Lassi",
                        "description": "Sweet yogurt drink",
                        "price": 60.00,
                        "category": "beverage",
                        "image_url": "https://source.unsplash.com/800x600/?lassi"
                    }
                ],
                "Girls Hostel Mess": [
                    {
                        "name": "Vegetable Pulao",
                        "description": "Rice cooked with mixed vegetables",
                        "price": 120.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?vegetable-rice"
                    },
                    {
                        "name": "Green Tea",
                        "description": "Healthy green tea with lemon",
                        "price": 40.00,
                        "category": "beverage",
                        "image_url": "https://source.unsplash.com/800x600/?green-tea"
                    },
                    {
                        "name": "Fruit Custard",
                        "description": "Creamy custard with fresh fruits",
                        "price": 90.00,
                        "category": "dessert",
                        "image_url": "https://source.unsplash.com/800x600/?fruit-custard"
                    }
                ],
                "Boys Hostel Mess": [
                    {
                        "name": "Chicken Tikka",
                        "description": "Grilled spicy chicken pieces",
                        "price": 180.00,
                        "category": "main",
                        "image_url": "https://source.unsplash.com/800x600/?grilled-chicken"
                    },
                    {
                        "name": "Cold Coffee",
                        "description": "Chilled coffee with ice cream",
                        "price": 100.00,
                        "category": "beverage",
                        "image_url": "https://source.unsplash.com/800x600/?iced-coffee"
                    },
                    {
                        "name": "Gulab Jamun",
                        "description": "Deep-fried milk dumplings in sugar syrup",
                        "price": 70.00,
                        "category": "dessert",
                        "image_url": "https://source.unsplash.com/800x600/?indian-dessert"
                    }
                ]
            }

            # Add menu items for each restaurant
            for restaurant_name, items in menu_items.items():
                restaurant_id = created_restaurants[restaurant_name]
                for item_data in items:
                    item_data['restaurant_id'] = restaurant_id
                    menu_item = MenuItem(**item_data)
                    db.session.add(menu_item)

            db.session.commit()
            logging.info("Sample restaurants and menu items added successfully")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initializing sample data: {str(e)}")

with app.app_context():
    init_sample_data()

@app.route('/orders')
@login_required
def order_history():
    try:
        orders = Order.query.filter_by(user_id=current_user.id)\
            .order_by(Order.created_at.desc())\
            .all()
        return render_template('orders/history.html', orders=orders)
    except Exception as e:
        logging.error(f"Error fetching order history: {str(e)}")
        flash('Error loading order history')
        return redirect(url_for('index'))

@app.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()

        # Get order items with menu item details
        order_items = OrderItem.query\
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)\
            .filter(OrderItem.order_id == order_id)\
            .all()

        order_items_list = []
        for item in order_items:
            order_items_list.append({
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.price * item.quantity
            })

        return render_template('orders/details.html', 
                            order=order,
                            order_items=order_items_list)
    except Exception as e:
        logging.error(f"Error fetching order details: {str(e)}")
        flash('Error loading order details')
        return redirect(url_for('order_history'))