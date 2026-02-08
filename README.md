🚀 Smart Study Assistant

An Academic Productivity Platform built using Flask, Machine Learning, and OCR.

Developed by Vedant Mishra

📖 Overview

Smart Study Assistant is a full-stack web application designed to enhance student learning through automation and intelligent insights.

The system integrates:
	•	📄 Optical Character Recognition (OCR) for extracting text from notes
	•	🧠 Machine Learning for grade prediction
	•	📝 Automated Quiz Generation
	•	📊 Performance Analytics and Visualization

It demonstrates the practical implementation of AI + ML + Web Technologies in an academic environment.

⸻

🏗 System Architecture

User Interface (CTK)
            ↓
        Flask Backend
            ↓
   ┌───────────────────────┐
   │  OCR Module           │
   │  (Pytesseract)        │
   ├───────────────────────┤
   │  ML Module            │
   │  (Scikit-learn)       │
   ├───────────────────────┤
   │  Visualization Module │
   │  (Matplotlib)         │
   └───────────────────────┘

✨ Key Features

📤 Note Upload System
	•	Secure file upload handling
	•	Supports image-based notes
	•	Stored in structured directory

🔍 OCR Text Extraction
	•	Converts handwritten/printed notes into machine-readable text
	•	Implemented using pytesseract

📝 Quiz Generation
	•	Dynamic quiz rendering
	•	Automated answer evaluation
	•	Score calculation logic

🤖 Grade Prediction
	•	Linear Regression model (Scikit-learn)
	•	Input: Study metrics (hours/scores)
	•	Output: Predicted academic performance

📊 Data Visualization
	•	Performance graphs using Matplotlib
	•	Helps track improvement trends

⸻

🛠 Technology Stack

Backend
	•	Python
	•	Flask

Frontend
	•	HTML5
	•	CSS3
	•	JavaScript

Machine Learning
	•	Scikit-learn
	•	Pandas
	•	NumPy

OCR
	•	Tesseract OCR
	•	Pytesseract

Visualization
	•	Matplotlib

⸻

📂 Project Structure

Smart-Study-Assistant/
│
├── app.py
├── main_app.py
│
├── templates/
│   ├── index.html
│   ├── upload.html
│   ├── quiz.html
│   └── result.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── uploads/


⚙️ Installation & Setup

1️⃣ Clone Repository
git clone https://github.com/your-username/Smart-Study-Assistant.git
cd Smart-Study-Assistant

2️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

3️⃣ Install Dependencies
pip install flask scikit-learn matplotlib numpy pandas pillow pytesseract pdf2image

4️⃣ Install Tesseract OCR (Mac)
brew install tesseract

Verify installation:
tesseract --version

Open Terminal 1 : 
5️⃣ Run Application
python app.py  

Open in browser: http://127.0.0.1:5000/   (Paste this : it shows Backend is Running)

Open Terminal 2 : 
Run : python main_app.py

now this is Running...................! "Congratulations" you run this Web page 

🧠 Machine Learning Workflow
	1.	Data Collection
	2.	Data Cleaning
	3.	Feature Selection
	4.	Model Training (Linear Regression)
	5.	Prediction
	6.	Result Visualization

 🔐 Security Considerations
	•	File type validation
	•	Controlled upload directory
	•	Input validation for forms
	•	Error handling mechanisms

⸻

📈 Future Enhancements
	•	User Authentication System
	•	Database Integration (PostgreSQL / MySQL)
	•	NLP-based Intelligent Question Generator
	•	Cloud Deployment (Render / AWS / Azure)
	•	Dashboard Analytics with interactive charts

⸻

🎯 Use Cases
	•	Academic institutions
	•	Self-learning platforms
	•	EdTech prototypes
	•	AI-based productivity tools

⸻

👨‍💻 Author

Vedant Mishra
B.Tech CSE 
Skills: Python | Machine Learning | Full-Stack Development

⸻

📜 License

This project is developed for educational and academic purposes.


