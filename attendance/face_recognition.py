import cv2
import os
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Student, StudentImage
from datetime import datetime
from PIL import Image
from django.core.files import File
import time

# Folder to save student face images
IMAGE_SAVE_PATH = "media/student_images/"
if not os.path.exists(IMAGE_SAVE_PATH):
    os.makedirs(IMAGE_SAVE_PATH)

# Initialize ORB feature extractor
orb = cv2.ORB_create(nfeatures=500)

def extract_features(image):
    """Extract ORB keypoints and descriptors from a grayscale image."""
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return keypoints, descriptors

def match_faces(descriptors1, descriptors2):
    """Match descriptors using brute-force matcher and return match count."""
    if descriptors1 is None or descriptors2 is None:
        return 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    strong_matches = [m for m in matches if m.distance < 50]  # Matching threshold
    return len(strong_matches)

@csrf_exempt
def capture_face(request):
    """Capture student's face and store image if it's unique."""
    if request.method == "POST":
        sname = request.POST.get("sname")
        regno = request.POST.get("reg_no")
        phnno = request.POST.get("phn_no")
        class_name = request.POST.get("class_name")

        if not (sname and regno and phnno and class_name):
            return JsonResponse({"status": "error", "message": "All fields are required."})

        if Student.objects.filter(reg_no=regno).exists():
            return JsonResponse({"status": "error", "message": "Student with this Register Number already exists."})

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return JsonResponse({"status": "error", "message": "Unable to access webcam."})

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        captured_images = []
        image_count = 0
        max_images = 5
        start_time = time.time()

        while image_count < max_images:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                if time.time() - start_time > 1:
                    face_image = gray[y:y + h, x:x + w]
                    face_image = cv2.resize(face_image, (400, 400))

                    _, new_descriptors = extract_features(face_image)

                    duplicate_found = False
                    for student_image in StudentImage.objects.all():
                        if not os.path.exists(student_image.image.path):
                            continue
                        stored_face = cv2.imread(student_image.image.path, cv2.IMREAD_GRAYSCALE)
                        if stored_face is None:
                            continue
                        stored_face = cv2.resize(stored_face, (400, 400))
                        _, stored_descriptors = extract_features(stored_face)

                        if match_faces(stored_descriptors, new_descriptors) > 10:
                            duplicate_found = True
                            break

                    if duplicate_found:
                        cap.release()
                        cv2.destroyAllWindows()
                        return JsonResponse({
                            "status": "error",
                            "message": "Duplicate face detected. Face already registered."
                        })

                    image_path = os.path.join(IMAGE_SAVE_PATH, f"{regno}_{image_count}.jpg")
                    Image.fromarray(face_image).save(image_path, "JPEG", quality=85)
                    captured_images.append(image_path)
                    image_count += 1
                    start_time = time.time()

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow("Capturing Face Automatically", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        student = Student(name=sname, reg_no=regno, phone_no=phnno, class_name=class_name, date=datetime.now())
        student.save()

        for i, image_path in enumerate(captured_images):
            with open(image_path, 'rb') as img_file:
                student_image = StudentImage(reg_no=student)
                student_image.image.save(f"{regno}_{i}.jpg", File(img_file))
                student_image.save()

        return JsonResponse({"status": "success", "message": f"{image_count} images captured automatically."})

    return render(request, "face_recognition.html")
