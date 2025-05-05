import os
from datetime import datetime, timedelta
from fpdf import FPDF
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Attendance, Student, AttendanceReport


def calculate_attendance_percentage(reg_no, start_date, end_date=None):
    """Calculate attendance percentage and half-day absences for a student."""
    if not end_date:
        end_date = start_date  # If no range, set single date
    
    attendance_records = Attendance.objects.filter(reg_no=reg_no, date__range=(start_date, end_date))

    total_days = (end_date - start_date).days + 1  # Include end_date
    daily_absence = {}

    for record in attendance_records:
        date_str = record.date.strftime("%Y-%m-%d")
        if date_str not in daily_absence:
            daily_absence[date_str] = {"morning": False, "afternoon": False}

        if record.session == "morning" and record.status == "absent":
            daily_absence[date_str]["morning"] = True
        if record.session == "afternoon" and record.status == "absent":
            daily_absence[date_str]["afternoon"] = True

    half_day_absences = sum(1 for day in daily_absence.values() if any(day.values()))
    present_days = total_days - half_day_absences  # Days without half-day absence
    max_leave_days = 27  # 30% of 90 days
    remaining_leaves = max(0, max_leave_days - half_day_absences)

    percentage = (present_days / total_days) * 100 if total_days > 0 else 0

    return {
        "present": present_days,
        "half_day_absent": half_day_absences,
        "leave": remaining_leaves,
        "percentage": round(percentage, 2),
    }

def generate_report_pdf(reg_no, start_date, end_date=None):
    """Generate a PDF attendance report and store it in the database."""
    try:
        student = Student.objects.get(reg_no=reg_no)
    except ObjectDoesNotExist:
        return None  # Student not found

    attendance_data = calculate_attendance_percentage(reg_no, start_date, end_date)

    # 🟩 STEP 1: Save report data into AttendanceReport model
    AttendanceReport.objects.create(
        reg_no=student,
        present_days=attendance_data["present"],
        full_day_present=attendance_data["present"],  # Assuming full day present = present days
        half_day_present=0,  # Optional: Add logic if needed
        half_day_absent=attendance_data["half_day_absent"],
        full_day_absent=0,  # Optional: Add logic if needed
        remaining_leave_days=attendance_data["leave"],
        percentage=attendance_data["percentage"],
        date=datetime.today() if not end_date else end_date
    )

    # 🟦 STEP 2: Generate the PDF report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Attendance Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Student Name: {student.name}", ln=True)
    pdf.cell(200, 10, f"Register No: {student.reg_no}", ln=True)
    pdf.cell(200, 10, f"Class: {student.class_name}", ln=True)
    pdf.cell(200, 10, f"Phone: {student.phone_no}", ln=True)

    if end_date:
        pdf.cell(200, 10, f"Report Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", ln=True)
    else:
        pdf.cell(200, 10, f"Report Date: {start_date.strftime('%Y-%m-%d')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Attendance Summary", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Full-Day Present: {attendance_data['present']}", ln=True)
    pdf.cell(200, 10, f"Half-Day Absences: {attendance_data['half_day_absent']}", ln=True)
    pdf.cell(200, 10, f"Remaining Leave Days: {attendance_data['leave']}", ln=True)
    pdf.cell(200, 10, f"Attendance Percentage: {attendance_data['percentage']}%", ln=True)

    # Ensure reports directory exists
    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    file_name = f"{reg_no}_{start_date.strftime('%Y-%m-%d')}.pdf" if not end_date else f"{reg_no}_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.pdf"
    file_path = os.path.join(reports_dir, file_name)

    pdf.output(file_path, "F")
    return file_path
