from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config import Config
from models import db, migrate, User
from users import Users
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        stage = request.form['stage']
        photos = request.files.getlist('photos')
        photo_paths = []
        for photo in photos:
            path = os.path.join('uploads', photo.filename)
            photo.save(path)
            photo_paths.append(path)
        result = "QueryManager().process_photos(stage, photo_paths)"
        # Save result to the database (not implemented here)
    return render_template('dashboard.html')

@app.route('/guest')
def guest():
    # Fetch all businesses and their photos/results (not implemented here)
    businesses = []
    return render_template('guest.html', businesses=businesses)

# @app.route('/report')
# def report():
#     report = Utils().generate_report()
#     return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
