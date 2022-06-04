from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


# Create A Form Class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Creat a Route Decorator


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

# Create name page


@app.route('/name', methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validite form
    if form.validate_on_submit:
        name = form.name.data
        form.name.data = ""
    return render_template('name.html', name=name, form=form)
