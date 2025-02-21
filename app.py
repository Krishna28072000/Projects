import os
import fitz  # PyMuPDF for PDF text extraction
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_scan_type(report_text):
    """Detects the type of scan from the report text (case insensitive)."""
    scan_keywords = {
        "MRI": ["MRI", "magnetic resonance imaging"],
        "CT Scan": ["CT scan", "computed tomography"],
        "X-ray": ["X-RAY", "radiograph"],
        "Ultrasound": ["ultrasound", "sonography"],
        "PET Scan": ["PET scan", "positron emission tomography"],
        "Mammogram": ["mammogram", "mammography"],
        "ECG": ["ECG", "electrocardiogram"],
        "EEG": ["EEG", "electroencephalogram"]
    }

    lower_text = report_text.lower()

    for scan, keywords in scan_keywords.items():
        for keyword in keywords:
            if keyword.lower() in lower_text:
                return scan
    return "Unknown Scan"

def analyze_text(report_text):
    """Classifies the report as Normal or Abnormal and provides recommendations."""
    abnormal_keywords = [
        "lesion", "tumor", "fracture", "abnormal", "malignant",
        "cancer", "growth", "irregular", "anomaly", "mass",
        "nodule", "metastasis", "calcification", "hemorrhage", "infection"
    ]  

    is_abnormal = any(keyword in report_text.lower() for keyword in abnormal_keywords)
    status = "Abnormal" if is_abnormal else "Normal"

    # Enhanced Recommendations
    if is_abnormal:
        recommendation = (
            "Follow up with a specialist for further examination. Additional tests such as biopsy or imaging might be required."
        )
    else:
        recommendation = (
            "No immediate concerns detected, but maintain regular health checkups."
        )

    return {"status": status, "recommendation": recommendation}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_pdf", methods=["POST"])
def analyze():
    """Handles file upload and analysis"""
    if "pdf_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["pdf_file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file format. Please upload a PDF"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    report_text = extract_text_from_pdf(file_path)

    if "Error reading PDF" in report_text:
        return jsonify({"error": report_text}), 500

    scan_type = extract_scan_type(report_text)
    result = analyze_text(report_text)
    
    result["scan"] = scan_type  # Add scan type to response

    return jsonify(result)

if __name__ == "__main__":
    print("Medical Analyzer running at http://127.0.0.1:5000/")
    app.run(debug=True)
# import os 
# import fitz 
# from flask import Flask, render_template, request, jsonify 

# app = Flask(__name__)

# UPLOAD_FOLDER = "uploads"
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
    
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# def extract_text_from_pdf(pdf_path):
#     """Extract text from given PDF file"""
#     try:
#         doc = fitz.open(pdf_path)
#         text = ""
#         for page in doc:
#             text += page.get_text("text") + "\n"
#         return text.strip()
#     except Exception as e:
#         return f"Error reading PDF: {str(e)}"

# def extract_scan_type(report_text):
#     """Detects the type of scan from the report text."""
#     scan_keywords = {
#         "MRI": ["MRI", "Magnetic Resonance Imaging"],
#         "CT Scan": ["CT scan", "Computed Tomography"],
#         "X-ray": ["X-RAY", "Radiograph"],
#         "Ultrasound": ["Ultrasound", "Sonography"],
#         "PET Scan": ["PET scan", "Positron Emission Tomography"],
#         "Mammogram": ["Mammogram", "Mammography"]
#     }

#     for scan, keywords in scan_keywords.items():
#         for keyword in keywords:
#             if keyword in report_text.lower():
#                 return scan
#     return "Unknown Scan"

# def analyze_text(report_text):
#     """Basic text-based classification: Normal or Abnormal."""
#     abnormal_keywords = [
#     "lesion","tumor","fracture","abnormal","malignant",
#     "cancer","growth","irregular","anomaly","mass" 
#     ] 
#     is_abnormal = any(keyword in report_text.lower() for keyword in abnormal_keywords)
    
#     status = "Abnormal" if is_abnormal else "Normal"
#     recommendation = (
#         "Follow up with a specialist for further examination" if is_abnormal
#         else " No immediate concerns, but maintain regular checkups."
        
#     )
#     return{"status": status, "recommendation": recommendation}

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/analyze_pdf", methods = ["POST"])
# def analyze():
#     """Handles file upload and analysis"""
#     if "pdf_file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400
    
#     file = request.files["pdf_file"]
    
#     if file.filename == "":
#         return jsonify({"error": "No file selected"}), 400
    
#     if not file.filename.endswith(".pdf"):
#         return jsonify({"error": "invalid file format. Please upload a PDF"}), 400
    
#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(file_path)
    
#     report_text = extract_text_from_pdf(file_path)
    
#     if "Error reading PDF" in report_text:
#         return jsonify({"error": report_text}), 500
    
#     result = analyze_text(report_text)
    
#     return jsonify(result)

# if __name__ == "__main__":
#     print("Medical Analyzer running at http://127.0.0.1:5000/")
#     app.run(debug=True)