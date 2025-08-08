from tkinter import messagebox
import random
import json
import gui as gui
import db as db

# Initialize the SQLite database tables.
db.initialize_database()

# quiz app
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Quiz App")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.config(bg="#abcefa")
        self.username = None
        self.score = 0
        self.current_question_index = 0
        self.selected_questions = []
        self.option_buttons = []
        self.username_entry = None
        self.submit_btn = None
        self.answer_var = None
        self.show_start_page()

    def show_start_page(self):
        gui.create_start_page(self.root, self)

    def start_app(self):
        self.show_login_frame()

    def show_login_frame(self):
        gui.create_login_frame(self.root, self)

    # show user login message
    def login_user(self):
        if not self.username_entry:
            return
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Error", "Username cannot be empty.")
            return

        # Use the SQLite db module to check and insert users
        user = db.get_user_by_username(username)
        if not user:
            db.insert_user(username)
            messagebox.showinfo("Welcome", "User registered and logged in.")
        else:
            messagebox.showinfo("Welcome", "User logged in.")

        self.username = username
        self.show_menu_frame()

    def show_menu_frame(self):
        gui.create_menu_frame(self.root, self)

    # get all random 5 questions from question database
    def start_quiz(self):
        try:
            # Load questions from the JSON file into the SQLite database first
            with open('questions.json', 'r') as f:
                questions_data = json.load(f)
                db.load_questions_from_json(questions_data)
        except FileNotFoundError:
            messagebox.showerror("Error", "questions.json not found. Please create the file.")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding questions.json. Please check file format.")
            return

        # Get the questions from the SQLite database
        all_questions = db.get_all_questions()

        if len(all_questions) < 5:
            messagebox.showerror("Error", "Not enough questions in the database (need at least 5).")
            return

        self.selected_questions = random.sample(all_questions, 5)
        self.score = 0
        self.current_question_index = 0
        self.show_question()

    def show_question(self):
        gui.create_question_frame(self.root, self)

    # check answers
    def check_answer(self):
        if self.answer_var.get() == -1:
            messagebox.showwarning("Warning", "Please select an answer before submitting.")
            return
        selected = self.answer_var.get()
        correct = self.selected_questions[self.current_question_index]['answer']
        if selected == correct:
            self.score += 1
        for i, btn in enumerate(self.option_buttons):
            btn.config(state="disabled")
            if i == correct:
                btn.config(bg="lightgreen", fg="black")
        self.submit_btn.config(state="disabled")
        self.root.after(1000, self.next_question)

    # next question
    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index < 5:
            self.show_question()
        else:
            self.finish_quiz()

    # end the quiz
    def finish_quiz(self):
        percent = int((self.score / 5) * 100)
        # Use the SQLite db module to insert the result
        db.insert_result(self.username, self.score, percent)
        gui.create_quiz_result_frame(self.root, self)

    # view your own score
    def view_scores(self):
        # Use the SQLite db module to get results
        user_results = db.get_user_results(self.username)
        all_results = db.get_all_results()
        gui.create_scores_frame(self.root, self, user_results, all_results)