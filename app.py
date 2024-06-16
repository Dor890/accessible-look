import os

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from PIL import Image as PillowImage

from config import Config
from models import db, migrate, User, Image, supported_places

from sqlalchemy.exc import IntegrityError

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
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')

        # Validate required fields
        if not username or not password:
            error_message = "שם המשתמש והסיסמה הם שדות חובה. אנא מלא אותם."
        else:
            # Handle file upload
            if 'main_image' in request.files:
                main_image = request.files['main_image']
                if main_image.filename == '':
                    error_message = "יש להעלות תמונה ראשית."
                else:
                    # Validate image file type (optional)
                    if not main_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        error_message = "יש להעלות קובץ תמונה בפורמט PNG, JPG, JPEG או GIF."

                    # Limit image size and resize if necessary
                    try:
                        max_image_size = (500, 500)  # Max width and height
                        image = PillowImage.open(main_image)
                        image.thumbnail(max_image_size, PillowImage.ANTIALIAS)
                        # Save resized image to a secure location
                        filename = secure_filename(main_image.filename)
                        upload_folder = os.path.join(app.root_path, 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)
                        image.save(file_path)
                    except Exception as e:
                        error_message = f"Failed to process image: {e}"

            else:
                error_message = "לא נמצאה תמונה ראשית בבקשה."

            # If no errors, proceed with user registration
            if not error_message:
                try:
                    user = User(username=username, password=password, name=name, main_image=file_path)
                    db.session.add(user)
                    db.session.commit()
                    print(f"User {username} registered successfully.")
                    return redirect(url_for('login'))
                except Exception as e:
                    error_message = f"Failed to register user: {e}"

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
    can_create_review = user.can_create_review()
    # Check if user can create a review

    if request.method == 'POST':
        place = request.form['place']
        photos = request.files.getlist('photos')

        if len(photos) < 3 or len(photos) > 5:
            flash('You must upload 3-5 photos for each place.', 'error')
            return redirect(url_for('dashboard'))

        # Directory where images will be saved
        save_directory = os.path.join('saved_photos', str(user.id), place)
        os.makedirs(save_directory, exist_ok=True)

        for photo in photos:
            # Secure the filename
            filename = secure_filename(photo.filename)

            # Define the path to save the file
            file_path = os.path.join(save_directory, filename)

            # Save the file to the specified directory
            photo.save(file_path)

            # Save image to the database
            new_image = Image(filepath=file_path, user_id=user.id, place=place)
            db.session.add(new_image)

        # Query the place and update user data
        user.query_and_update_place(place)

        # Commit changes to the database
        db.session.commit()

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


@app.route('/download_report')
def download_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user'])
    if not user.final_result:
        flash('Report not available. Please ensure all places have been reviewed.', 'error')
        return redirect(url_for('dashboard'))

    try:
        return send_file(user.pdf_report_path, as_attachment=True, download_name='Accessibility_Report.pdf')
    except FileNotFoundError:
        flash('Report file not found. Please try again later.', 'error')
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


@app.route('/add_test_user')
def add_test_user():
    user = User(username='testuser@gmail.com', password='password')
    db.session.add(user)
    db.session.commit()  # Commit changes to the database session
    print("Test user added successfully.")
    return redirect(url_for('login'))  # Redirect to another route or return a response


if __name__ == '__main__':
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True)
