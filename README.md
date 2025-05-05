Face Recognition Based Attendance System
This project implements a Face Recognition Based Attendance System using Python and OpenCV. The system automatically marks attendance by recognizing faces from a live camera feed. It enhances traditional attendance methods by providing a touchless, fast, and reliable solution.

📘 Table of Contents
Features

Technologies Used

System Architecture

Installation

Usage

Project Modules

Screenshots

Advantages

Limitations

Future Enhancements

Authors

✅ Features
Live face detection and recognition

Automatic attendance logging

Stores data with timestamps in a CSV or pdf file

GUI for user interaction

No Admin and no security

Access all student 

Accurate and fast processing

🛠️ Technologies Used
Python

OpenCV

NumPy

face_recognition

MySQL (for database storage)

dlib

🧩 System Architecture
Student Registration: Capture and store facial images linked to a unique ID.

Training Data: Train the recognition model using stored face data.

Face Recognition: Detect and recognize faces in real-time using the trained model.

Attendance Logging: Mark attendance and save date-time logs in a CSV file.

Report: download and view the report.

💻 Installation
Clone the repository

bash
Copy
Edit
git clone https://github.com/yourusername/face-recognition-attendance.git
cd face-recognition-attendance
Install dependencies

bash
Copy
Edit
pip install opencv-python numpy pillow face_recognition cmake dlib mysqlclient
Run the application

bash
Copy
Edit
python main.py
▶️ Usage
Launch the application.

Register a new student by capturing face images.

Train the model with the captured images.

Start attendance and let the system recognize faces and mark attendance.

View attendance logs in the admin panel.

📂 Project Modules
media/ — Stores face images

Report — Attendance records

main.py — Main application script

face_recognition.py — Core recognition module and register student data with images

attendance.py — Student mark attendance(morning/afternoon)

report.py — 90days report 

gui.py — Graphical interface

📸 Screenshots
(Include screenshots here from your application GUI if available)

👍 Advantages
Eliminates proxy attendance

Time-efficient and automatic

Easy to use GUI

No need for manual verification

⚠️ Limitations
Works best under good lighting conditions

Requires high-resolution webcam for accuracy

Performance may degrade with masks or accessories on faces

🔮 Future Enhancements
Add cloud storage integration

Improve recognition accuracy using deep learning (e.g., FaceNet, Dlib)

Enable email notifications

Android/iOS mobile application integration

👨‍💻 Authors
Santhoshkumar T M - Developer and Project Lead

Madura College - Madurai(Tamilnadu) / M.Sc.CS

