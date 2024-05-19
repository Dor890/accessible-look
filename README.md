# accessible-look

## Accessibility Checker for Business Photos

### Overview
This project allows users to upload photos of specific parts of their business to determine if they are accessible for individuals with disabilities. The analysis is performed using the OpenAI API, which provides feedback on the accessibility features depicted in the uploaded images.

### Features
Photo Upload: Users can upload photos of areas in their business.

Accessibility Analysis: Utilizes the OpenAI API to evaluate the photos for accessibility features.
Results Feedback: Provides users with detailed feedback on the accessibility status of the photographed areas.
### Prerequisites
Before running this project, ensure you have the following:
Python 3.8 or higher

An OpenAI API key

The following Python libraries:

Flask

Requests

Pillow

Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/accessibility-checker.git
cd accessibility-checker
Install the required libraries:

bash
Copy code
pip install -r requirements.txt
Set up environment variables:
Create a .env file in the root directory and add your OpenAI API key:

plaintext
Copy code
OPENAI_API_KEY=your_openai_api_key
Usage
Run the Flask server:

bash
Copy code
python app.py
Open your web browser and navigate to:

arduino
Copy code
http://127.0.0.1:5000
Upload a photo:

Click on the "Upload Photo" button.
Select a photo from your device.
Submit the photo for analysis.
View Results:

The server will process the image using the OpenAI API.
After processing, you will receive feedback on the accessibility of the area shown in the photo.
Project Structure
app.py: The main Flask application file.
requirements.txt: List of dependencies.
templates/: HTML templates for the web interface.
static/: Static files (e.g., CSS, JavaScript).
uploads/: Directory where uploaded photos are temporarily stored.
Example
Uploading a Photo
Select a Photo:

Receive Analysis:

Contributing
If you would like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-branch).
Open a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
For questions or suggestions, please open an issue in the repository or contact the project maintainer:

Name: Your Name
Email: your.email@example.com
Thank you for using the Accessibility Checker for Business Photos. Your contributions and feedback are welcome to help improve this project!