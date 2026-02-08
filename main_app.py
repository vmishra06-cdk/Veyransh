import customtkinter
import requests
import threading
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import qrcode
import io
import webbrowser
from tkinter import filedialog
import pandas as pd
from tkinter import messagebox

# A dictionary to simulate a QR/proximity database
MOCK_PROXIMITY_DB = {
    "C101": ["S001", "S002"],
    "C102": ["S003"],
}

# A dictionary to simulate a facial recognition database
MOCK_FACE_DB = {
    "S001": [np.zeros((10, 10), dtype=np.uint8)], # Placeholder for face embeddings
    "S002": [np.zeros((10, 10), dtype=np.uint8)],
}

# Pre-populated data - This will be updated with CSV upload
STUDENT_NAMES = {
    "S001": "Alice Johnson", "S002": "Bob Smith", "S003": "Charlie Brown",
    "S004": "Diana Prince", "S005": "Ethan Hunt", "S006": "Fiona Glenanne",
    "S007": "George Costanza", "S008": "Holly Golightly", "S009": "Isaac Asimov",
    "S010": "Jane Doe", "S011": "Kevin Malone", "S012": "Larry David",
    "S013": "Marge Simpson", "S014": "Ned Flanders", "S015": "Olivia Pope",
    "S016": "Peter Parker", "S017": "Quinn Fabray", "S018": "Rachel Green",
    "S019": "Sheldon Cooper", "S020": "Tina Belcher"
}

COURSE_NAMES = {
    "C101": "Introduction to Python",
    "C102": "Data Structures",
    "C103": "Web Development",
    "C104": "Database Systems",
    "C105": "Machine Learning"
}


class App(customtkinter.CTk):
    """
    Main application class for the attendance and productivity tool.
    This UI will communicate with the Flask backend.
    """
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")

        self.title("Student Productivity App")
        self.geometry("1200x900")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.attendance_vars = {}
        self.students_textbox = None
        self.courses_textbox = None

        # NEW: Main tab view for organizing the UI
        self.tab_view = customtkinter.CTkTabview(self, width=1160, height=860)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Create tabs
        self.attendance_tab = self.tab_view.add("Attendance")
        self.schedule_tasks_tab = self.tab_view.add("Schedule & Tasks")
        self.performance_tab = self.tab_view.add("Performance")
        self.manage_data_tab = self.tab_view.add("Manage Data")
        self.about_tab = self.tab_view.add("About & Resources")

        # Configure tab layouts
        self.attendance_tab.grid_columnconfigure(0, weight=1)
        self.attendance_tab.grid_rowconfigure(0, weight=1)
        self.schedule_tasks_tab.grid_columnconfigure((0, 1), weight=1)
        self.schedule_tasks_tab.grid_rowconfigure(0, weight=1)
        self.performance_tab.grid_columnconfigure((0, 1), weight=1)
        self.performance_tab.grid_rowconfigure(0, weight=1)
        self.manage_data_tab.grid_columnconfigure((0, 1), weight=1)
        self.manage_data_tab.grid_rowconfigure(0, weight=1)
        self.about_tab.grid_columnconfigure((0, 1), weight=1)
        self.about_tab.grid_rowconfigure(0, weight=1)
        
        #
        # --- Attendance Tab Content ---
        #
        self.attendance_frame = customtkinter.CTkFrame(self.attendance_tab)
        self.attendance_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.attendance_frame.grid_columnconfigure(0, weight=1)
        
        customtkinter.CTkLabel(self.attendance_frame, text="Mark Attendance", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        self.class_id_entry = customtkinter.CTkEntry(self.attendance_frame, placeholder_text="Class ID (e.g., C101)")
        self.class_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.checkbox_frame = customtkinter.CTkScrollableFrame(self.attendance_frame)
        self.checkbox_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.checkbox_frame.grid_columnconfigure(0, weight=1)
        
        self.load_student_checkboxes()

        customtkinter.CTkButton(self.attendance_frame, text="Mark Selected Attendance", command=self.mark_selected_attendance_thread).grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        customtkinter.CTkButton(self.attendance_frame, text="Auto Mark Attendance (Simulated)", command=self.auto_mark_attendance_thread).grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.attendance_status_label = customtkinter.CTkLabel(self.attendance_frame, text="", wraplength=300)
        self.attendance_status_label.grid(row=5, column=0, padx=10, pady=10)
        self.attendance_frame.grid_rowconfigure(2, weight=1)

        #
        # --- Schedule & Tasks Tab Content ---
        #
        self.schedule_frame = customtkinter.CTkFrame(self.schedule_tasks_tab)
        self.schedule_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.schedule_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self.schedule_frame, text="Daily Schedule", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        self.schedule_student_id_entry = customtkinter.CTkEntry(self.schedule_frame, placeholder_text="Student ID (e.g., S001)")
        self.schedule_student_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        customtkinter.CTkButton(self.schedule_frame, text="Get Schedule", command=self.get_schedule_thread).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.schedule_display = customtkinter.CTkTextbox(self.schedule_frame, width=300, height=200)
        self.schedule_display.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tasks_frame = customtkinter.CTkFrame(self.schedule_tasks_tab)
        self.tasks_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.tasks_frame.grid_columnconfigure(0, weight=1)
        
        customtkinter.CTkLabel(self.tasks_frame, text="Personalized Tasks", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)

        self.tasks_student_id_entry = customtkinter.CTkEntry(self.tasks_frame, placeholder_text="Student ID (e.g., S001)")
        self.tasks_student_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        customtkinter.CTkButton(self.tasks_frame, text="Get Tasks", command=self.get_tasks_thread).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.tasks_display = customtkinter.CTkTextbox(self.tasks_frame, width=300, height=200)
        self.tasks_display.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        #
        # --- Performance Tab Content ---
        #
        self.performance_frame = customtkinter.CTkFrame(self.performance_tab)
        self.performance_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.performance_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self.performance_frame, text="Performance Graph", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        self.graph_student_id_entry = customtkinter.CTkEntry(self.performance_frame, placeholder_text="Student ID (e.g., S001)")
        self.graph_student_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        customtkinter.CTkButton(self.performance_frame, text="Generate Performance Graph", command=self.generate_performance_graph_thread).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.graph_image_label = customtkinter.CTkLabel(self.performance_frame, text="", width=400, height=300)
        self.graph_image_label.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        self.realtime_frame = customtkinter.CTkFrame(self.performance_tab)
        self.realtime_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.realtime_frame.grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(self.realtime_frame, text="Real-Time Attendance", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        
        self.realtime_class_id_entry = customtkinter.CTkEntry(self.realtime_frame, placeholder_text="Class ID (e.g., C101)")
        self.realtime_class_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        customtkinter.CTkButton(self.realtime_frame, text="Get Real-Time Attendance", command=self.get_realtime_attendance_thread).grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.realtime_display = customtkinter.CTkTextbox(self.realtime_frame, width=300, height=200)
        self.realtime_display.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        #
        # --- Manage Data Tab Content ---
        #
        self.manage_frame = customtkinter.CTkFrame(self.manage_data_tab)
        self.manage_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.manage_frame.grid_columnconfigure((0, 1), weight=1)
        
        customtkinter.CTkLabel(self.manage_frame, text="Manage Student & Course Data", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10, columnspan=2)

        self.student_id_manage_entry = customtkinter.CTkEntry(self.manage_frame, placeholder_text="Student ID (e.g., S021)")
        self.student_id_manage_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.student_name_manage_entry = customtkinter.CTkEntry(self.manage_frame, placeholder_text="Student Name")
        self.student_name_manage_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        customtkinter.CTkButton(self.manage_frame, text="Add Student", command=self.add_student).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(self.manage_frame, text="Remove Student", command=self.remove_student).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.course_id_manage_entry = customtkinter.CTkEntry(self.manage_frame, placeholder_text="Course ID (e.g., C106)")
        self.course_id_manage_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.course_name_manage_entry = customtkinter.CTkEntry(self.manage_frame, placeholder_text="Course Name")
        self.course_name_manage_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        customtkinter.CTkButton(self.manage_frame, text="Add Course", command=self.add_course).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(self.manage_frame, text="Remove Course", command=self.remove_course).grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.data_frame = customtkinter.CTkFrame(self.manage_data_tab)
        self.data_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.data_frame.grid_columnconfigure(0, weight=1)
        
        customtkinter.CTkLabel(self.data_frame, text="Student & Course Data", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)

        self.students_textbox = customtkinter.CTkTextbox(self.data_frame, height=200, width=300)
        self.students_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.students_textbox.insert("1.0", "Students:\n\n" + "\n".join([f"{k}: {v}" for k, v in STUDENT_NAMES.items()]))
        self.students_textbox.configure(state="disabled")

        self.courses_textbox = customtkinter.CTkTextbox(self.data_frame, height=200, width=300)
        self.courses_textbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.courses_textbox.insert("1.0", "Courses:\n\n" + "\n".join([f"{k}: {v}" for k, v in COURSE_NAMES.items()]))
        self.courses_textbox.configure(state="disabled")

        #
        # --- About & Resources Tab Content ---
        #
        self.about_frame = customtkinter.CTkFrame(self.about_tab)
        self.about_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(3, weight=1)
        
        customtkinter.CTkLabel(self.about_frame, text="About & Resources", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10, columnspan=2)

        self.gemini_button = customtkinter.CTkButton(self.about_frame, text="Get Suggestions from Gemini 🤖", command=self.open_gemini_url)
        self.gemini_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.csv_upload_button = customtkinter.CTkButton(self.about_frame, text="Upload Student/Course Data (CSV)", command=self.upload_csv)
        self.csv_upload_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.qr_code_frame = customtkinter.CTkFrame(self.about_tab)
        self.qr_code_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.qr_code_frame.grid_columnconfigure(0, weight=1)
        
        customtkinter.CTkLabel(self.qr_code_frame, text="Generate QR Code", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=10)
        self.qr_student_id_entry = customtkinter.CTkEntry(self.qr_code_frame, placeholder_text="Student ID (e.g., S001)")
        self.qr_student_id_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        customtkinter.CTkButton(self.qr_code_frame, text="Generate QR Code", command=self.generate_qr_code).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.qr_image_label = customtkinter.CTkLabel(self.qr_code_frame, text="")
        self.qr_image_label.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.qr_code_frame.grid_rowconfigure(3, weight=1)
        self.about_tab.grid_columnconfigure(1, weight=1)


    def update_textboxes(self):
        """Helper function to update the student and course textboxes."""
        if self.students_textbox:
            self.students_textbox.configure(state="normal")
            self.students_textbox.delete("1.0", "end")
            self.students_textbox.insert("1.0", "Students:\n\n" + "\n".join([f"{k}: {v}" for k, v in STUDENT_NAMES.items()]))
            self.students_textbox.configure(state="disabled")

        if self.courses_textbox:
            self.courses_textbox.configure(state="normal")
            self.courses_textbox.delete("1.0", "end")
            self.courses_textbox.insert("1.0", "Courses:\n\n" + "\n".join([f"{k}: {v}" for k, v in COURSE_NAMES.items()]))
            self.courses_textbox.configure(state="disabled")

    def add_student(self):
        student_id = self.student_id_manage_entry.get().upper()
        student_name = self.student_name_manage_entry.get()
        if not student_id or not student_name:
            messagebox.showerror("Error", "Please enter both student ID and name.")
            return

        if student_id in STUDENT_NAMES:
            response = messagebox.askyesno("Confirm Update", f"Student ID {student_id} already exists. Do you want to update the name?")
            if not response:
                return

        STUDENT_NAMES[student_id] = student_name
        self.update_textboxes()
        self.load_student_checkboxes()
        requests.post("http://127.0.0.1:5000/update_data", json={"students": STUDENT_NAMES, "courses": COURSE_NAMES})
        messagebox.showinfo("Success", f"Student {student_id} ({student_name}) has been added/updated.")

    def remove_student(self):
        student_id = self.student_id_manage_entry.get().upper()
        if not student_id:
            messagebox.showerror("Error", "Please enter a student ID to remove.")
            return

        if student_id in STUDENT_NAMES:
            del STUDENT_NAMES[student_id]
            self.update_textboxes()
            self.load_student_checkboxes()
            requests.post("http://127.0.0.1:5000/update_data", json={"students": STUDENT_NAMES, "courses": COURSE_NAMES})
            messagebox.showinfo("Success", f"Student {student_id} has been removed.")
        else:
            messagebox.showerror("Error", f"Student ID {student_id} not found.")

    def add_course(self):
        course_id = self.course_id_manage_entry.get().upper()
        course_name = self.course_name_manage_entry.get()
        if not course_id or not course_name:
            messagebox.showerror("Error", "Please enter both course ID and name.")
            return

        if course_id in COURSE_NAMES:
            response = messagebox.askyesno("Confirm Update", f"Course ID {course_id} already exists. Do you want to update the name?")
            if not response:
                return

        COURSE_NAMES[course_id] = course_name
        self.update_textboxes()
        requests.post("http://127.0.0.1:5000/update_data", json={"students": STUDENT_NAMES, "courses": COURSE_NAMES})
        messagebox.showinfo("Success", f"Course {course_id} ({course_name}) has been added/updated.")

    def remove_course(self):
        course_id = self.course_id_manage_entry.get().upper()
        if not course_id:
            messagebox.showerror("Error", "Please enter a course ID to remove.")
            return

        if course_id in COURSE_NAMES:
            del COURSE_NAMES[course_id]
            self.update_textboxes()
            requests.post("http://127.0.0.1:5000/update_data", json={"students": STUDENT_NAMES, "courses": COURSE_NAMES})
            messagebox.showinfo("Success", f"Course {course_id} has been removed.")
        else:
            messagebox.showerror("Error", f"Course ID {course_id} not found.")

    def load_student_checkboxes(self):
        """ Clears and re-populates the checkbox frame with students. """
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        
        self.attendance_vars = {}
        row = 0
        for student_id, name in STUDENT_NAMES.items():
            var = customtkinter.StringVar(value="off")
            self.attendance_vars[student_id] = var
            checkbox = customtkinter.CTkCheckBox(self.checkbox_frame, text=f"{student_id} - {name}", variable=var, onvalue="on", offvalue="off")
            checkbox.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            row += 1

    def open_gemini_url(self):
        """ Opens a web browser to the Gemini URL. """
        webbrowser.open("https://gemini.google.com")

    def upload_csv(self):
        """ Prompts the user to select a CSV file and loads the data. """
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            
            if 'student_id' in df.columns and 'name' in df.columns:
                global STUDENT_NAMES
                new_students = {row['student_id']: row['name'] for _, row in df.iterrows()}
                STUDENT_NAMES.update(new_students)
                self.update_textboxes()
                self.load_student_checkboxes()
            
            if 'course_id' in df.columns and 'name' in df.columns:
                global COURSE_NAMES
                new_courses = {row['course_id']: row['name'] for _, row in df.iterrows()}
                COURSE_NAMES.update(new_courses)
                self.update_textboxes()

            requests.post("http://127.0.0.1:5000/update_data", json={"students": STUDENT_NAMES, "courses": COURSE_NAMES})
            
            self.attendance_status_label.configure(text=f"Successfully loaded data from {file_path}", text_color="green")
            
        except Exception as e:
            self.attendance_status_label.configure(text=f"Error loading CSV file: {e}", text_color="red")
            print(f"CSV error: {e}")

    def mark_selected_attendance_thread(self):
        threading.Thread(target=self.mark_selected_attendance).start()

    def mark_selected_attendance(self):
        class_id = self.class_id_entry.get()
        if not class_id:
            self.attendance_status_label.configure(text="Please enter a Class ID.", text_color="red")
            return

        selected_students = [
            student_id for student_id, var in self.attendance_vars.items()
            if var.get() == "on"
        ]

        if not selected_students:
            self.attendance_status_label.configure(text="No students selected.", text_color="orange")
            return
        
        self.attendance_status_label.configure(text="Marking attendance...", text_color="blue")

        try:
            for student_id in selected_students:
                data = {"student_id": student_id, "class_id": class_id}
                response = requests.post("http://127.0.0.1:5000/attendance", json=data)
                response.raise_for_status()
            
            message = f"Attendance marked for: {', '.join(selected_students)}"
            self.attendance_status_label.configure(text=message, text_color="green")
            
        except requests.exceptions.RequestException as e:
            self.attendance_status_label.configure(text=f"Error: Could not connect to the server. Is the Flask app running?", text_color="red")
            print(f"Connection error: {e}")
        except Exception as e:
            self.attendance_status_label.configure(text=f"An unexpected error occurred: {e}", text_color="red")
            print(f"Unexpected error: {e}")

    def auto_mark_attendance_thread(self):
        threading.Thread(target=self.auto_mark_attendance).start()

    def auto_mark_attendance(self):
        self.attendance_status_label.configure(text="Simulating auto attendance marking...", text_color="blue")
        time.sleep(1)
        current_class_id = "C101"
        present_students_proximity = MOCK_PROXIMITY_DB.get(current_class_id, [])
        self.attendance_status_label.configure(text=f"Proximity scan found: {present_students_proximity}", text_color="blue")
        time.sleep(1)
        present_students_face = []
        for student_id, _ in MOCK_FACE_DB.items():
            if student_id in present_students_proximity:
                present_students_face.append(student_id)
        
        if present_students_face:
            self.attendance_status_label.configure(text=f"Facial recognition verified: {present_students_face}", text_color="blue")
        else:
            self.attendance_status_label.configure(text="No students verified by facial recognition.", text_color="orange")
        verified_students = list(set(present_students_proximity) & set(present_students_face))
        if verified_students:
            for student_id in verified_students:
                data = {"student_id": student_id, "class_id": current_class_id}
                try:
                    response = requests.post("http://127.0.0.1:5000/attendance", json=data)
                    response.raise_for_status()
                    print(f"Attendance marked for {student_id}")
                except requests.exceptions.RequestException as e:
                    print(f"Error marking attendance for {student_id}: {e}")
            self.attendance_status_label.configure(text=f"Auto attendance marked for: {', '.join(verified_students)}", text_color="green")
        else:
            self.attendance_status_label.configure(text="No students could be automatically marked present.", text_color="red")
    
    def get_realtime_attendance_thread(self):
        threading.Thread(target=self.get_realtime_attendance).start()

    def get_realtime_attendance(self):
        class_id = self.realtime_class_id_entry.get()
        if not class_id:
            self.realtime_display.delete("1.0", "end")
            self.realtime_display.insert("1.0", "Please enter a Class ID.")
            return

        try:
            response = requests.get(f"http://127.0.0.1:5000/realtime_attendance/{class_id}")
            response.raise_for_status()
            
            attendance_data = response.json()
            self.realtime_display.delete("1.0", "end")
            self.realtime_display.insert("1.0", f"Real-Time Attendance for {class_id}:\n\n")
            if attendance_data:
                for student_id, status in attendance_data.items():
                    self.realtime_display.insert("end", f"- {student_id}: {status}\n")
            else:
                self.realtime_display.insert("end", "No attendance data available.")
        except requests.exceptions.RequestException:
            self.realtime_display.delete("1.0", "end")
            self.realtime_display.insert("1.0", "Error: Could not connect to the server.")

    def generate_performance_graph_thread(self):
        threading.Thread(target=self.generate_performance_graph).start()
    
    def generate_performance_graph(self):
        student_id = self.graph_student_id_entry.get()
        if not student_id:
            self.graph_image_label.configure(text="Please enter a Student ID.", image=None)
            return
        
        weeks = list(range(1, 11))
        scores = np.random.randint(60, 100, size=10)
        
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(4, 3))
        plt.plot(weeks, scores, marker='o', linestyle='-', color='cyan')
        plt.title(f'Performance for {student_id}', fontsize=12)
        plt.xlabel('Week', fontsize=10)
        plt.ylabel('Score (%)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        
        graph_img = Image.open(buf)
        graph_img_tk = customtkinter.CTkImage(light_image=graph_img, dark_image=graph_img, size=(400, 300))
        self.graph_image_label.configure(image=graph_img_tk, text="")
        self.graph_image_label.image = graph_img_tk
        
    def generate_qr_code(self):
        student_id = self.qr_student_id_entry.get()
        if not student_id:
            self.qr_image_label.configure(text="Please enter a Student ID.", image=None)
            return
        if student_id not in STUDENT_NAMES:
            messagebox.showerror("Error", f"Student ID '{student_id}' not found.")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(student_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_tk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(200, 200))
        self.qr_image_label.configure(image=img_tk, text="")
        self.qr_image_label.image = img_tk
        
    def generate_routine_thread(self):
        threading.Thread(target=self.generate_routine).start()

    def generate_routine(self):
        student_id = self.routine_student_id_entry.get()
        if not student_id:
            self.routine_display.delete("1.0", "end")
            self.routine_display.insert("1.0", "Please enter a Student ID.")
            return
        
        try:
            response = requests.get(f"http://127.0.0.1:5000/daily_routine/{student_id}")
            response.raise_for_status()
            routine_data = response.json()
            
            self.routine_display.delete("1.0", "end")
            self.routine_display.insert("1.0", f"Daily Routine for {student_id}:\n\n")
            for item in routine_data:
                self.routine_display.insert("end", f"Time: {item['time']}\nActivity: {item['activity']}\n\n")
        
        except requests.exceptions.RequestException:
            self.routine_display.delete("1.0", "end")
            self.routine_display.insert("1.0", "Error: Could not connect to the server.")

    def get_schedule_thread(self):
        threading.Thread(target=self.get_schedule).start()
        
    def get_schedule(self):
        student_id = self.schedule_student_id_entry.get()
        if not student_id:
            self.schedule_display.delete("1.0", "end")
            self.schedule_display.insert("1.0", "Please enter a Student ID.")
            return

        try:
            response = requests.get(f"http://127.0.0.1:5000/schedule/{student_id}")
            response.raise_for_status()
            
            schedule_data = response.json()
            if not isinstance(schedule_data, list):
                self.schedule_display.delete("1.0", "end")
                self.schedule_display.insert("1.0", "Error: Expected a list of classes. Please check the backend.")
                return

            self.schedule_display.delete("1.0", "end")
            self.schedule_display.insert("1.0", f"Schedule for {student_id}:\n\n")
            for item in schedule_data:
                self.schedule_display.insert("end", f"Class: {item['class']}\nTime: {item['time']}\n\n")
                
        except requests.exceptions.HTTPError as e:
            self.schedule_display.delete("1.0", "end")
            if e.response.status_code == 404:
                self.schedule_display.insert("1.0", "Student schedule not found.")
            else:
                self.schedule_display.insert("1.0", f"HTTP Error: {e.response.status_code}")
        except requests.exceptions.RequestException:
            self.schedule_display.delete("1.0", "end")
            self.schedule_display.insert("1.0", "Error: Could not connect to the server.")
        except Exception as e:
            self.schedule_display.delete("1.0", "end")
            self.schedule_display.insert("1.0", f"An unexpected error occurred: {e}")

    def get_tasks_thread(self):
        threading.Thread(target=self.get_tasks).start()

    def get_tasks(self):
        student_id = self.tasks_student_id_entry.get()
        
        if not student_id:
            self.tasks_display.delete("1.0", "end")
            self.tasks_display.insert("1.0", "Please enter a Student ID.")
            return

        try:
            response = requests.get(f"http://127.0.0.1:5000/tasks/{student_id}")
            response.raise_for_status()
            
            tasks_data = response.json()
            if not isinstance(tasks_data, list):
                self.tasks_display.delete("1.0", "end")
                self.tasks_display.insert("1.0", "Error: Expected a list of tasks. Please check the backend.")
                return

            self.tasks_display.delete("1.0", "end")
            self.tasks_display.insert("1.0", f"Personalized Tasks for {student_id}:\n\n")
            for task in tasks_data:
                self.tasks_display.insert("end", f"- {task}\n")
                
        except requests.exceptions.HTTPError as e:
            self.tasks_display.delete("1.0", "end")
            if e.response.status_code == 404:
                self.tasks_display.insert("1.0", "No personalized tasks found for this student.")
            else:
                self.tasks_display.insert("1.0", f"HTTP Error: {e.response.status_code}")
        except requests.exceptions.RequestException:
            self.tasks_display.delete("1.0", "end")
            self.tasks_display.insert("1.0", "Error: Could not connect to the server.")
        except Exception as e:
            self.tasks_display.delete("1.0", "end")
            self.tasks_display.insert("1.0", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
