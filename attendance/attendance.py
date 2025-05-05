# attendance.py
import cv2
import os
import json
import numpy as np
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import StudentImage, Attendance

orb = cv2.ORB_create(nfeatures=500)

def extract_features(image):
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def match_faces(descriptors1, descriptors2):
    if descriptors1 is None or descriptors2 is None:
        return 0
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    strong_matches = [m for m in matches if m.distance < 50]
    return len(strong_matches)

@csrf_exempt
def take_attendance(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    try:
        request_data = json.loads(request.body)
        session_requested = request_data.get("session")
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data."})

    now = datetime.now()
    today_date = now.date()
    current_hour = now.hour
    current_minute = now.minute

    # Session validation
    if session_requested == "morning" and current_hour >= 12:
        return JsonResponse({"status": "error", "message": "This is not the morning session."})
    if session_requested == "afternoon" and current_hour < 12:
        return JsonResponse({"status": "error", "message": "This is not the afternoon session."})

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JsonResponse({"status": "error", "message": "Unable to access webcam."})

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    recognized_student = None

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

                if matches > best_match_score and matches > 10:
                    best_match_score = matches
                    best_match_student = student_image.student

            if best_match_student:
                recognized_student = best_match_student
                cv2.putText(frame, recognized_student.name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Face Recognition", frame)

        if recognized_student:
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not recognized_student:
        return JsonResponse({"status": "error", "message": "Face not recognized."})

    # Time slots
    time_slots = {
        "morning": [
            ("1st_hour", (8, 45), (9, 40)),
            ("2nd_hour", (9, 45), (10, 40)),
            ("3rd_hour", (10, 45), (11, 40))
        ],
        "afternoon": [
            ("4th_hour", (12, 20), (13, 15)),
            ("5th_hour", (13, 20), (14, 15))
        ]
    }

    session_periods = time_slots.get(session_requested, [])
    status = "absent"
    period_marked = None

    for period, (start_h, start_m), (end_h, end_m) in session_periods:
        start_time = start_h * 60 + start_m
        end_time = end_h * 60 + end_m
        current_time = current_hour * 60 + current_minute

        if start_time <= current_time <= end_time:
            status = "present"
            period_marked = period
            break

    if not period_marked:
        return JsonResponse({"status": "error", "message": "No valid attendance period at this time."})

    already_marked = Attendance.objects.filter(
        reg_no=recognized_student,
        session=session_requested,
        period=period_marked,
        date=today_date
    ).exists()

    if already_marked:
        return JsonResponse({
            "status": "error",
            "message": f"{recognized_student.name} is already marked for {period_marked} in {session_requested} session today."
        })

    Attendance.objects.create(
        reg_no=recognized_student,
        session=session_requested,
        period=period_marked,
        status=status,
        date=today_date
    )

    return JsonResponse({
        "status": "success",
        "message": f"{recognized_student.name} marked {status} for {period_marked} in {session_requested} session."
    })

def attendance_page(request):
    return render(request, "attendance.html")
