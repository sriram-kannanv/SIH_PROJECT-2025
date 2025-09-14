from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(200))
    adhaar = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    username = db.Column(db.String(50))
    password = db.Column(db.String(200))
    gmail = db.Column(db.String(200))

with app.app_context():
    db.create_all()


# Google OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="392983736227-135mkvor4qq39bna62l8epjip6v9djas.apps.googleusercontent.com",
    client_secret="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",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)



@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
@app.route('/login/callback')
def callback():
    token = google.authorize_access_token()
    user_info = google.userinfo()   # ✅ correct way
    session['user'] = user_info
    return redirect(url_for('form'))


@app.route('/form', methods=['GET', 'POST'])
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    gmail = session['user']['email']
    google_id = session['user'].get('id') or session['user'].get('sub')

    if request.method == 'POST':
        # ✅ Check if this user already exists
        existing_user = User.query.filter_by(google_id=google_id).first()

        if existing_user:
            # Update existing user details
            existing_user.name = request.form['name']
            existing_user.adhaar = request.form['adhaar']
            existing_user.dob = request.form['dob']
            existing_user.gender = request.form['gender']
            existing_user.mobile = request.form['mobile']
            existing_user.username = request.form['username']
            existing_user.password = request.form['password']
            existing_user.gmail = gmail
        else:
            # Create new user
            user = User(
                google_id=google_id,
                name=request.form['name'],
                adhaar=request.form['adhaar'],
                dob=request.form['dob'],
                gender=request.form['gender'],
                mobile=request.form['mobile'],
                username=request.form['username'],
                password=request.form['password'],
                gmail=gmail
            )
            db.session.add(user)

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template("form.html", gmail=gmail)


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template("dashboard.html", name=session['user']['name'])

if __name__ == '__main__':
    app.run(debug=True)
