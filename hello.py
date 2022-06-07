import email
from importlib.resources import contents
from wsgiref.handlers import format_date_time
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea


# Create a Flask Instance
app = Flask(__name__)
# Add database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users1.db'
# MYSQL database link
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password147@localhost/our_users1'
# Secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Initialise the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Creat a Blog Post Model


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# Create a posts form


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[
                          DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/posts')
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)

    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


# Add posts page


@app.route('/add-post',  methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear the form.
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""
        # Add data to database
        db.session.add(post)
        db.session.commit()
        flash('Post was submitted successfully')

    # Redirect to the webpage
    return render_template('add_post.html', form=form)

# Creat a model


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_colour = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readble attribute!!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string

    def __repr__(self):
        return '<name %r>' % self.name


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('Whoops. Something went wrong deleting the user...rty again!!!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users, id=id)

# Create A Form Class


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_colour = StringField("Favourite Colour")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo(
        'password_hash2', message='Passwords Must Match')])
    password_hash2 = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# Update database record


@app.route('/update/<int:id>', methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        try:
            db.session.commit()
            flash('User Updated Successfully!!')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            db.session.commit()
            flash('Error!! Looks like there was a problem..... try again!')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
# Create A Form Class


class PasswordForm(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password_hash = PasswordField(
        "What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Creat a Route Decorator


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(
                form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data,
                         favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        form.favourite_colour.data = ""
        form.password_hash.data = ""
        flash('User Added Successfully!!!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/')
def index():
    first_name = 'keith'
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', username=name)

# create custom error page
# invalid URL


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# invalid URL


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# Create Password Test Page


@app.route('/test_pw', methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ""
        form.password_hash.data = ""

        # Look up user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password=password, form=form, passed=passed, pw_to_check=pw_to_check)

# Create name page


@app.route('/name', methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validite form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash('Form Submitted Successfully!')
    return render_template('name.html', name=name, form=form)
