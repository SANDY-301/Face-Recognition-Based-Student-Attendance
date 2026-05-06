import cv2
import os
import numpy as np
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import StudentImage, Attendance

# ORB feature detector
orb = cv2.ORB_create()

def extract_features(image):
    """Extracts ORB keypoints and descriptors from an image."""
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def match_faces(descriptors1, descriptors2):
    """Matches ORB descriptors using the BFMatcher."""
    if descriptors1 is None or descriptors2 is None:
        return 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    return len(matches)

@csrf_exempt
def take_attendance(request):
    """
    Marks attendance based on ORB face recognition.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JsonResponse({"status": "error", "message": "Unable to access webcam."})

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return JsonResponse({"status": "error", "message": "Failed to capture image."})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    recognized_student = None
    max_matches = 0

    for (x, y, w, h) in faces:
        face_roi = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, (400, 400))

        # Extract ORB features from captured face
        _, captured_descriptors = extract_features(face_roi)

        for student_image in StudentImage.objects.all():
            image_path = student_image.image.path

            if not os.path.exists(image_path):
                continue

            stored_face = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            stored_face = cv2.resize(stored_face, (400, 400))

            # Extract ORB features from stored image
            _, stored_descriptors = extract_features(stored_face)

            matches = match_faces(stored_descriptors, captured_descriptors)

            if matches > max_matches:
                max_matches = matches
                recognized_student = student_image.student

        if recognized_student:
            break

    if not recognized_student:
        return JsonResponse({"status": "error", "message": "Face not recognized."})

    # Determine session and status
    now = datetime.now()
    session = "morning" if now.hour < 12 else "afternoon"
    status = "present" if now.hour < 9 else "late" if now.hour < 9.15 else "absent"

    # Save attendance record
    attendance = Attendance(reg_no=recognized_student, session=session, status=status, date=now)
    attendance.save()

    return JsonResponse({"status": "success", "message": f"{recognized_student.name} marked {status} for {session} session."})

# Render attendance page
def attendance_page(request):
    return render(request, "attendance.html")


import cv2
import os
import json
import numpy as np
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import StudentImage, Attendance

orb = cv2.ORB_create(nfeatures=500)  # Use more features for better matching

def extract_features(image):
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def match_faces(descriptors1, descriptors2):
    """Match ORB descriptors with a threshold."""
    if descriptors1 is None or descriptors2 is None:
        return 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches by distance (lower distance means better match)
    matches = sorted(matches, key=lambda x: x.distance)

    # Return only strong matches (distance threshold)
    strong_matches = [m for m in matches if m.distance < 50]  # Adjust threshold as needed
    return len(strong_matches)

@csrf_exempt
def take_attendance(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # ✅ Load JSON properly
    try:
        request_data = json.loads(request.body)
        session_requested = request_data.get("session")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data."})

    # ✅ Check session timing
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    if session_requested == "morning" and current_hour >= 12:
        return JsonResponse({"status": "error", "message": "This is not the morning session."})
    if session_requested == "afternoon" and current_hour < 12:
        return JsonResponse({"status": "error", "message": "This is not the afternoon session."})

    # ✅ Open webcam and detect face
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JsonResponse({"status": "error", "message": "Unable to access webcam."})

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    recognized_student = None
    max_matches = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (400, 400))
            _, captured_descriptors = extract_features(face_roi)

            best_match_student = None
            best_match_score = 0

            for student_image in StudentImage.objects.all():
                image_path = student_image.image.path
                if not os.path.exists(image_path):
                    continue

                stored_face = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                stored_face = cv2.resize(stored_face, (400, 400))
                _, stored_descriptors = extract_features(stored_face)

                matches = match_faces(stored_descriptors, captured_descriptors)
                
                # Only consider if it exceeds a minimum threshold
                if matches > best_match_score and matches > 10:  # Set a minimum match threshold
                    best_match_score = matches
                    best_match_student = student_image.student

            if best_match_student:
                recognized_student = best_match_student
                cv2.putText(frame, recognized_student.name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.8, (0, 255, 0), 2, cv2.LINE_AA)
                break  # Stop after the first recognized face

        cv2.imshow("Face Recognition", frame)
        
        if recognized_student:
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not recognized_student:
        return JsonResponse({"status": "error", "message": "Face not recognized."})

    # ✅ Determine attendance based on time
    time_slots = {
        "morning": [
            ("1st_hour", 8, 45, 8, 50),
            ("2nd_hour", 9, 45, 9, 46),
            ("3rd_hour", 10, 45, 10, 46)
        ],
        "afternoon": [
            ("4th_hour", 12, 20, 12, 25),
            ("5th_hour", 13, 20, 13, 21)
        ]
    }

    session_periods = time_slots.get(session_requested, [])
    status = "absent"
    period_marked = None

    for period, start_h, start_m, end_h, end_m in session_periods:
        if (current_hour == start_h and start_m <= current_minute <= end_m):
            status = "present"
            period_marked = period
            break
        elif current_hour > end_h or (current_hour == end_h and current_minute > end_m):
            period_marked = period

    if not period_marked:
        return JsonResponse({"status": "error", "message": "No valid attendance period."})

    # ✅ Save attendance
    Attendance.objects.create(reg_no=recognized_student, session=session_requested, period=period_marked, status=status)

    return JsonResponse({
        "status": "success",
        "message": f"{recognized_student.name} marked {status} for {period_marked} in {session_requested} session."
    })

# Render attendance page
def attendance_page(request):
    return render(request, "attendance.html")
