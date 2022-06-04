from flask import Flask, render_template

# Create a Flask Instance
app = Flask(__name__)

# Creat a Route Decorator


@app.route('/')
def index():
    first_name = 'Keith'
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
def name(name):
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
