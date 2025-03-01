from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Restaurant, MenuItem
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