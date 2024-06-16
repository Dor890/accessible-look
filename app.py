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
    message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')

        # Validate required fields
        if not is_valid_email(username):
            error_message = "שם המשתמש חייב להיות בפורמט של כתובת דואר אלקטרוני תקפה."
        elif len(name) < 3:
            error_message = "שם העסק חייב להכיל לפחות 3 תווים."
        elif len(password) < 6:
            error_message = "הסיסמה חייבת להכיל לפחות 6 תווים."
        else:
            # Handle file upload
            if 'main_image' in request.files:
                main_image = request.files['main_image']
                # Validate image file type (optional)
                if not main_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    error_message = "יש להעלות קובץ תמונה בפורמט PNG, JPG, JPEG או GIF."

                # Limit image size and resize if necessary
                try:
                    filename = secure_filename(main_image.filename)
                    # Save file to a secure location, adjust as needed
                    upload_folder = os.path.join(app.root_path, 'main_images', username)
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    main_image.save(file_path)
                except Exception as e:
                    error_message = "העלאת התמונה נכשלה."

            else:
                error_message = "על מנת להירשם לאתר יש להעלות תמונה ראשית של העסק."

            # If no errors, proceed with user registration
            if not error_message:
                try:
                    user = User(username=username, password=password, name=name, address=address)
                    db.session.add(user)
                    db.session.commit()
                    user.add_main_image(file_path)
                    message = "ההרשמה בוצעה בהצלחה! אנא התחבר."
                    return redirect(url_for('login', message=message))
                except Exception as e:
                    error_message = f"Failed to register user: {e}"

    return render_template('register.html', error_message=error_message)


def is_valid_email(email):
    # Function to validate email format
    # You can add more robust email validation as per your requirements
    return '@' in email and '.' in email


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    message = request.args.get('message')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = user.id
            return redirect(url_for('dashboard'))
        else:
            error_message = "שם המשתמש או הסיסמה אינם נכונים. אנא נסה שוב."

    return render_template('login.html', error_message=error_message, message=message)


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

    if request.method == 'POST':
        place = request.form['place']
        photos = request.files.getlist('photos')

        if len(photos) < 3 or len(photos) > 5:
            error_message = 'You must upload 3-5 photos for each place.'
            return render_template('dashboard.html', user=user, supported_places=supported_places,
                                   can_create_review=can_create_review, error_message=error_message)

        save_directory = os.path.join('saved_photos', str(user.id), place)
        os.makedirs(save_directory, exist_ok=True)

        for photo in photos:
            filename = secure_filename(photo.filename)
            file_path = os.path.join(save_directory, filename)
            photo.save(file_path)
            new_image = Image(filepath=file_path, user_id=user.id, place=place)
            db.session.add(new_image)

        user.query_and_update_place(place)
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


@app.route('/business/<int:user_id>')
def business_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('business_details.html', user=user)


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
    user = User(username='testuser@gmail.com', password='password', name="בדיקה", address="בדיקה", )
    db.session.add(user)
    db.session.commit()  # Commit changes to the database session
    print("Test user added successfully.")
    return redirect(url_for('login'))  # Redirect to another route or return a response


if __name__ == '__main__':
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(debug=True)
