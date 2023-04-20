import os
import openai
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


# Set up OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'candymagic'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutriai.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    profile = db.relationship('UserProfile', backref='user', uselist=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Meal {self.name}>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(50), nullable=False)
    dietary_preferences = db.Column(db.String(100), nullable=True)
    allergies = db.Column(db.String(100), nullable=True)
    health_goal = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"UserProfile('{self.id}', '{self.gender}', '{self.health_goal}')"


# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("That username is already taken. Please choose a different one.", "warning")
        elif existing_email:
            flash("That email is already in use. Please choose a different one.", "warning")
        else:
            # Create new user
            user = User(username=form.username.data, email=form.email.data)
            user.password_hash = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created! Please complete your profile.", "success")
            return redirect(url_for('create_profile'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if not user.profile:
                flash("Please complete your profile.", "info")
                return redirect(url_for('create_profile'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/create_profile", methods=["GET" ,"POST"])
@login_required
def create_profile():
    if current_user.profile:
        return redirect(url_for("dashboard"))
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        height = request.form['height']
        activity_level = request.form['activity_level']
        dietary_preferences = request.form['dietary_preferences']
        allergies = request.form['allergies']
        health_goal = request.form['health_goal']

        userprofile = UserProfile(user_id=current_user.id, age=age, gender=gender, weight=weight, height=height,
                                    activity_level=activity_level, dietary_preferences=dietary_preferences,
                                    allergies=allergies, health_goal=health_goal)
        db.session.add(userprofile)

        db.session.commit()
        flash('Profile created successfully!')
        return redirect(url_for('dashboard'))
    return render_template('create_profile.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        height = request.form['height']
        activity_level = request.form['activity_level']
        dietary_preferences = request.form['dietary_preferences']
        allergies = request.form['allergies']
        health_goal = request.form['health_goal']

        userprofile = UserProfile.query.filter_by(user_id=current_user.id).first()

        if userprofile:
            userprofile.age = age
            userprofile.gender = gender
            userprofile.weight = weight
            userprofile.height = height
            userprofile.activity_level = activity_level
            userprofile.dietary_preferences = dietary_preferences
            userprofile.allergies = allergies
            userprofile.health_goal = health_goal
        else:
            userprofile = UserProfile(user_id=current_user.id, age=age, gender=gender, weight=weight, height=height,
                                        activity_level=activity_level, dietary_preferences=dietary_preferences,
                                        allergies=allergies, health_goal=health_goal)
            db.session.add(userprofile)

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))

    userprofile = UserProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('profile.html', profile=userprofile)

def calculate_tdee(user):
    # Constants for the Mifflin-St Jeor equation
    if user.gender == "male":
        base_bmr = 88.362
        weight_factor = 13.397
        height_factor = 4.799
        age_factor = 5.677
    else:  # assuming female
        base_bmr = 447.593
        weight_factor = 9.247
        height_factor = 3.098
        age_factor = 4.330

    bmr = base_bmr + (weight_factor * user.weight) + (height_factor * user.height) - (age_factor * user.age)

    activity_multiplier = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9,
    }

    tdee = bmr * activity_multiplier[user.activity_level]
    return tdee

def calculate_nutrient_goals(user):
    tdee = calculate_tdee(user)
    # Calculate macronutrient targets based on the user's health goals
    # You can customize these values based on the user's specific requirements
    protein_goal = user.weight * 1.8  # g/day
    fat_goal = user.weight * 0.8  # g/day
    carb_goal = (tdee - (protein_goal * 4 + fat_goal * 9)) / 4  # g/day

    return {
        "calories": tdee,
        "protein": protein_goal,
        "fat": fat_goal,
        "carbohydrates": carb_goal,
    }

def generate_meal_plans(meal_type, user, meal_description):
    nutrient_goals = calculate_nutrient_goals(user)
    dietary_preferences = user.dietary_preferences
    meal_plan = {}


    # meal_types = ["breakfast", "lunch", "dinner", "snack"]

    prompt = f"Generate a single {meal_type} meal plan that meets the following nutrient goals: {nutrient_goals} and caters to the dietary preferences: {dietary_preferences}, which {meal_description}. Include portion sizes for each meal."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.8,
    )

    meal_plan[meal_type] = response.choices[0].text.strip().split("\n")

    return meal_plan

@app.route('/generate_meal_plan', methods=['GET', 'POST'])
@login_required
def generate_meal_plan():
    meal_plan = None
    if request.method == "POST":
        user = UserProfile.query.filter_by(user_id=current_user.id).first()
        # meal_name = request.form['meal_name']
        meal_description = request.form['meal_description']
        meal_type = request.form['meal_type']
        meal_plan = generate_meal_plans(meal_type, user, meal_description)
        # meal = Meal(name=meal_name, description=meal_plan.values(), user_id=current_user.id)
        # db.session.add(meal)
        # db.session.commit()
        # flash('Meal added successfully!')
        # return redirect(url_for('generate_meal_plan'))
    return render_template('generate_meal_plan.html', meal_plan=meal_plan)


@app.route('/progress_tracking')
@login_required
def progress_tracking():
    return render_template('progress_tracking.html')


def generate_meal_ideas(diet, food_preferences):
    prompt = f"Generate meal ideas for someone who follows a {diet} diet and prefers {food_preferences}."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.8,
    )

    meal_ideas = response.choices[0].text.strip().split("\n")
    return meal_ideas

@app.route('/generate_recipe', methods=['GET', 'POST'])
@login_required
def generate_recipe():
    meal_ideas = None
    if request.method == "POST":
        diet = request.form['diet']
        food_preferences = request.form['food_preferences']
        meal_ideas = generate_meal_ideas(diet, food_preferences)
    
    return render_template('generate_recipe.html', meal_ideas=meal_ideas)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
    # from waitress import serve
    # serve(app, host="127.0.0.1", port=8080)