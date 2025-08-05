import tkinter as tk
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import uuid
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["quiz_app"]
users_collection = db["users"]
results_collection = db["results"]

questions_data = []


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Quiz App")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.config(bg="#abcefa")

        self.username = None
        self.user_id = None
        self.score = 0
        self.current_question_index = 0
        self.selected_questions = []
        self.option_buttons = []
        self.login_frame()

    def login_frame(self):
        self.clear()
        tk.Label(self.root, text="Enter Username:", font=("Arial", 14)).pack(pady=30)
        self.username_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.username_entry.pack(pady=10)
        tk.Button(self.root, text="Login/Register", command=self.login_user, width=20, height=2, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Exit", command=self.root.destroy, width=20, height=2, font=("Arial", 12)).pack(pady=10)

    def login_user(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Error", "Username cannot be empty.")
            return

        user = users_collection.find_one({"username": username})
        if not user:
            self.user_id = str(uuid.uuid4())
            users_collection.insert_one({"username": username})
            messagebox.showinfo("Welcome", "User registered and logged in.")
        else:
            self.username = user["username"]
            messagebox.showinfo("Welcome", "User logged in.")

        self.username = username
        self.menu_frame()

    def menu_frame(self):
        self.clear()
        tk.Label(self.root, text=f"Welcome, {self.username}!", font=("Arial", 20, "bold")).pack(pady=40)
        tk.Button(self.root, text="Take Quiz", command=self.start_quiz, width=25, height=3, font=("Arial", 14)).pack(pady=15)
        tk.Button(self.root, text="View Scores", command=self.view_scores, width=25, height=3, font=("Arial", 14)).pack(pady=15)
        tk.Button(self.root, text="Logout", command=self.login_frame, width=25, height=3, font=("Arial", 14)).pack(pady=15)

    def start_quiz(self):
        global questions_data
        if not questions_data:
            try:
                with open('questions.json', 'r') as f:
                    questions_data = json.load(f)
            except FileNotFoundError:
                messagebox.showerror("Error", "questions.json not found. Please create the file.")
                return
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Error decoding questions.json. Please check file format.")
                return

        if len(questions_data) < 5:
            messagebox.showerror("Error", "Not enough questions in the database (need at least 5).")
            return

        self.selected_questions = random.sample(questions_data, 5)
        self.score = 0
        self.current_question_index = 0
        self.option_buttons = []
        self.show_question()

    def show_question(self):
        self.clear()
        self.option_buttons = []
        q = self.selected_questions[self.current_question_index]

        tk.Label(self.root, text=f"Question {self.current_question_index + 1} of 5:", font=("Arial", 12, "italic")).pack(pady=10)
        tk.Label(self.root, text=q['question'], font=("Arial", 16), wraplength=700).pack(pady=20)

        self.answer_var = tk.IntVar()
        self.answer_var.set(-1)

        for idx, opt in enumerate(q['options']):
            btn = tk.Radiobutton(self.root, text=opt, variable=self.answer_var, value=idx, font=("Arial", 14),
                                 indicatoron=0, width=50, padx=10, pady=5, bd=2, relief="groove")
            btn.pack(anchor='center', pady=5)
            self.option_buttons.append(btn)

        self.submit_btn = tk.Button(self.root, text="Submit Answer", command=self.check_answer, width=20, height=2, font=("Arial", 12, "bold"))
        self.submit_btn.pack(pady=30)

    def check_answer(self):
        if self.answer_var.get() == -1:
            messagebox.showwarning("Warning", "Please select an answer before submitting.")
            return

        selected = self.answer_var.get()
        correct = self.selected_questions[self.current_question_index]['answer']

        if selected == correct:
            self.score += 1

        for btn in self.option_buttons:
            btn.config(state="disabled")

        for i, btn in enumerate(self.option_buttons):
            btn.config(state="disabled")  # Disable all buttons first

            if i == correct:
                btn.config(bg="lightgreen", fg="black")
            elif i == selected and selected != correct:
                btn.config(bg="red", fg="white")

        self.submit_btn.config(state="disabled")
        self.root.after(1500, self.next_question)

    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index < 5:
            self.show_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        percent = int((self.score / 5) * 100)
        msg = {
            0: "Better luck next time!",
            1: "Keep practicing!",
            2: "You're getting there!",
            3: "Good job!",
            4: "Excellent work!",
            5: "You are a genius!"
        }[self.score]

        results_collection.insert_one({
            "username": self.username,
            "user_id": self.user_id,
            "score": self.score,
            "percent": percent
        })

        self.clear()
        tk.Label(self.root, text="Quiz Complete!", font=("Arial", 20, "bold")).pack(pady=20)
        tk.Label(self.root, text=f"Your Score: {self.score}/5 ({percent}%)", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=msg, font=("Arial", 14, "italic")).pack(pady=10)

        if percent < 60:
            tk.Button(self.root, text="Retake Quiz", command=self.start_quiz, width=20, height=2, font=("Arial", 12)).pack(pady=15)
        tk.Button(self.root, text="Back to Menu", command=self.menu_frame, width=20, height=2, font=("Arial", 12)).pack(pady=15)

    def view_scores(self):
        self.clear()
        tk.Label(self.root, text="Your Quiz History", font=("Arial", 20, "bold")).pack(pady=15)
        user_results = list(results_collection.find({"user_id": self.user_id}))

        if not user_results:
            tk.Button(self.root, text="Back to Menu", command=self.menu_frame, width=20, height=2, font=("Arial", 12)).pack(pady=20)
            tk.Label(self.root, text="No quiz attempts yet. Take a quiz to see your scores!", font=("Arial", 14)).pack(pady=20)
        else:
            scores = [r['score'] for r in user_results]

            tk.Button(self.root, text="Back to Menu", command=self.menu_frame, width=20, height=2, font=("Arial", 12)).pack(pady=20)

            tk.Label(self.root, text=f"Total Quizzes: {len(user_results)}", font=("Arial", 12)).pack(pady=2)
            tk.Label(self.root, text=f"Average Score: {sum(scores) / len(scores):.2f}/5", font=("Arial", 12)).pack(pady=2)
            tk.Label(self.root, text=f"Your Highest Score: {max(scores)}/5", font=("Arial", 12)).pack(pady=2)
            tk.Label(self.root, text=f"Your Lowest Score: {min(scores)}/5", font=("Arial", 12)).pack(pady=2)

            all_results = list(results_collection.find())
            overall_highest_score = max([r['score'] for r in all_results]) if all_results else 0

            last_score = user_results[-1]['score']
            your_highest_score = max(scores)

            labels = ['Your Last Score', 'Your Highest Score', 'Overall Highest Score']
            values = [last_score, your_highest_score, overall_highest_score]
            colors = ['skyblue', 'lightcoral', 'lightgreen']

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(labels, values, color=colors)
            ax.set_ylim(0, 5)
            ax.set_ylabel('Score (out of 5)')
            ax.set_title('Your Performance Overview vs. Overall')

            for i, v in enumerate(values):
                ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold')

            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(pady=20)
            canvas.draw()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()