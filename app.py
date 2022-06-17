import email
from importlib.resources import contents
from wsgiref.handlers import format_date_time
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create a Flask Instance
app = Flask(__name__)
ckeditor = CKEditor(app)

# Add database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users1.db'
# MYSQL database link
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password147@localhost/our_users1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cqgzessyghgglw:afb7fa7ac9223255a10e5799c7edcd84dc9ccb6452df472179e51544d64ade78@ec2-52-72-56-59.compute-1.amazonaws.com:5432/d4djksrjmpfed1'
# Secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# Initialise the database
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 14:
        return render_template('admin.html')
    else:
        flash('Sorry you must be the Admin!')
        return redirect(url_for('dashboard'))

# Create search function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # get data from submitted form
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)



# Create login page.
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successful!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password- try again!')
        else:
            flash('That user does not exist - try again!')

    return render_template('login.html', form=form)
# Create logiut page
@app.route('/logout', methods=["GET", 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('login'))

# Create dashboard page
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favourite_colour = request.form['favourite_colour']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
       
        # Grab image name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
         # Save the image
        saver = request.files['profile_pic']
        # Change to a string to save to database
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            flash('User Updated Successfully!!')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            db.session.commit()
            flash('Error!! Looks like there was a problem..... try again!')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    return render_template('dashboard.html')

# Creat a Blog Post Model





@app.route('/posts')
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)

    return render_template('posts.html', posts=posts)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post Deleted Successfully!!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash('Whoops. Something went wrong deleting the post...rty again!!!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash('You are not authorised to delete this post!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=["GET", 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Add to database
        db.session.add(post)
        db.session.commit()
        flash('Post has been updated!!')
        return(redirect(url_for('post', id=post.id)))
    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash('You are not authorised to edit this post.')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# Add posts page


@app.route('/add-post',  methods=["GET", "POST"])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data, poster_id=poster, slug=form.slug.data)
        # Clear the form.
        form.title.data = ""
        form.content.data = ""
        #form.author.data = ""
        form.slug.data = ""
        # Add data to database
        db.session.add(post)
        db.session.commit()
        flash('Post was submitted successfully')

    # Redirect to the webpage
    return render_template('add_post.html', form=form)

# Creat a model





@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
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
    else:
        flash('You cannot delete that ID')
        return redirect(url_for('dashboard'))

# Create A Form Class




# Update database record


@app.route('/update/<int:id>', methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
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
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,favourite_colour=form.favourite_colour.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
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

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foreign key to lin users (refer to the primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favourite_colour = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(500), nullable=True)
    # Do some password stuff
    password_hash = db.Column(db.String())
    # User can have many posts
    posts = db.relationship('Posts', backref='poster')

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