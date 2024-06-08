from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, migrate, User, Image, supported_places

from sqlalchemy.exc import IntegrityError
from io import BytesIO
from PIL import Image as PILImage

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            print(f"User {username} registered successfully.")
            return redirect(url_for('login'))
        except IntegrityError:
            error_message = f"Username '{username}' already exists. Please choose a different username."
        except Exception as e:
            error_message = f"An error occurred: {e}"

    return render_template('register.html', error_message=error_message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear the session data (log out the user)
    session.pop('user', None)
    # Redirect the user to the homepage
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user'])
    can_create_review = user.can_create_review()  # Check if user can create a review

    if request.method == 'POST':
        place = request.form['place']
        photos = request.files.getlist('photos')

        if len(photos) < 3 or len(photos) > 5:
            flash('You must upload 3-5 photos for each place.', 'error')
            return redirect(url_for('dashboard'))

        for photo in photos:
            # Read image data
            image_stream = photo.read()

            # Create PIL image
            pil_image = PILImage.open(BytesIO(image_stream))

            # Resize if needed and convert to JPEG format
            pil_image = pil_image.resize((600, 600))  # Resize if needed
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            image_data = buffered.getvalue()

            # Save image to the database
            new_image = Image(data=image_data, filename=photo.filename, user_id=user.id, place=place)
            db.session.add(new_image)

        # Query the place and update user data
        user.query_and_update_place(place)

    return render_template('dashboard.html', user=user, supported_places=supported_places,
                           can_create_review=can_create_review)


@app.route('/create_review', methods=['POST'])
def create_review():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user'])

    # Check if user can create a review
    if user.can_create_review():
        # Execute the function to produce the final result
        user.produce_final_result()

        # Redirect to a page where the final review is displayed
        return redirect(url_for('dashboard'))
    else:
        flash('You need to upload images for all places before creating a review.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/guest')
def guest():
    users = User.query.all()
    users_with_places = [user for user in users if user.places]
    return render_template('guest.html', users=users_with_places)


@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/delete_user/<username>', methods=['POST'])
def delete_user(username):
    User.query.filter_by(username=username).delete()
    db.session.commit()

    return redirect(url_for('admin'))


# @app.route('/add_test_user')
# def add_test_user():
#     user = User(username='testuser@gmail.com', password='password')
#     db.session.add(user)
#     db.session.commit()  # Commit changes to the database session
#     print("Test user added successfully.")
#     return redirect(url_for('login'))  # Redirect to another route or return a response


if __name__ == '__main__':
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True)
