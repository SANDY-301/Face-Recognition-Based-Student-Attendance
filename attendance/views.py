from django.shortcuts import render
from django.http import JsonResponse
from .face_recognition import capture_face  # Make sure to import capture_face
import time 

def face_recognition_view(request):
    """
    Handle face recognition requests.
    """
    if request.method == "POST":
        # Instead of passing individual arguments, just pass the request object
        return capture_face(request)  # Pass the request object directly to capture_face

    # Render the face recognition page
    return render(request, "face_recognition.html")

def splash_view(request):
    time.sleep(3)  # 3 Seconds Delay for Splash Screen
    return render(request, "home.html")

def home_view(request):
    # Your logic here
    return render(request, 'home.html')

from django.shortcuts import render
from django.http import JsonResponse
from .attendance import take_attendance  # The method to handle attendance capturing

def attendance_view(request):
    """
    This view handles the display of the attendance page where users can choose morning or afternoon attendance.
    """
    if request.method == "POST":
        return take_attendance(request)  # Handle attendance marking logic here

    # Render the attendance page
    return render(request, "attendance.html")

from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from datetime import datetime
from .models import Student
from .report import generate_report_pdf, calculate_attendance_percentage

def report_view(request):
    return render(request, "report.html")

def generate_attendance_report(request):
    if request.method == "POST":
        reg_no = request.POST.get("reg_no")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date format."})

        student = Student.objects.filter(reg_no=reg_no).first()
        if not student:
            return JsonResponse({"status": "error", "message": "Student not found."})

        attendance_data = calculate_attendance_percentage(reg_no, start_date, end_date)

        return JsonResponse({"status": "success", "message": "Report generated successfully."})

    return JsonResponse({"status": "error", "message": "Invalid request method."})

def download_attendance_report(request):
    reg_no = request.GET.get("reg_no")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid date format."})

    file_path = generate_report_pdf(reg_no, start_date, end_date)
    return FileResponse(open(file_path, "rb"), as_attachment=True)


