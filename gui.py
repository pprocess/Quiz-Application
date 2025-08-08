import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def clear_frame(root):
    for widget in root.winfo_children():
        widget.destroy()

# starting page
def create_start_page(root, app_instance):
    clear_frame(root)
    tk.Label(root, text="Quiz Game", font=("Arial", 32, "bold"), bg=root['bg']).pack(pady=50)
    tk.Button(root, text="Start", command=app_instance.start_app, width=25, height=3, font=("Arial", 14)).pack(pady=15)
    tk.Button(root, text="Exit", command=root.destroy, width=25, height=3, font=("Arial", 14)).pack(pady=15)
    tk.Label(root, text="built by Process, Felipe, Ali", font=("Arial", 10), bg=root['bg']).pack(side="bottom", pady=20)

# login frame
def create_login_frame(root, app_instance):
    clear_frame(root)
    tk.Label(root, text="Enter Username:", font=("Arial", 14), bg=root['bg']).pack(pady=30)
    app_instance.username_entry = tk.Entry(root, width=30, font=("Arial", 12))
    app_instance.username_entry.pack(pady=10)
    tk.Button(root, text="Login/Register", command=app_instance.login_user, width=20, height=2,
              font=("Arial", 12)).pack(pady=10)
    tk.Button(root, text="Back", command=lambda: create_start_page(root, app_instance), width=20, height=2, font=("Arial", 12)).pack(pady=10)

# welcome menu
def create_menu_frame(root, app_instance):
    clear_frame(root)
    tk.Label(root, text=f"Welcome, {app_instance.username}!", font=("Arial", 20, "bold"), bg=root['bg']).pack(pady=40)
    tk.Button(root, text="Take Quiz", command=app_instance.start_quiz, width=25, height=3, font=("Arial", 14)).pack(
        pady=15)
    tk.Button(root, text="View Scores", command=app_instance.view_scores, width=25, height=3, font=("Arial", 14)).pack(
        pady=15)
    tk.Button(root, text="Logout", command=lambda: create_login_frame(root, app_instance), width=25, height=3,
              font=("Arial", 14)).pack(pady=15)

# show questions:
def create_question_frame(root, app_instance):
    clear_frame(root)
    tk.Button(root, text="Back", command=lambda: create_menu_frame(root, app_instance), width=10, height=2, font=("Arial", 12)).pack(anchor="nw", padx=10, pady=10)

    q = app_instance.selected_questions[app_instance.current_question_index]

    tk.Label(root, text=f"Question {app_instance.current_question_index + 1} of 5:", font=("Arial", 12, "italic"), bg=root['bg']).pack(pady=10)
    tk.Label(root, text=q['question'], font=("Arial", 16), wraplength=700, bg=root['bg']).pack(pady=20)

    app_instance.answer_var = tk.IntVar()
    app_instance.answer_var.set(-1)
    app_instance.option_buttons = []

    for idx, opt in enumerate(q['options']):
        btn = tk.Radiobutton(root, text=opt, variable=app_instance.answer_var, value=idx, font=("Arial", 14), indicatoron=0, width=50, padx=10, pady=5, bd=2, relief="groove")
        btn.pack(anchor='center', pady=5)
        app_instance.option_buttons.append(btn)

    app_instance.submit_btn = tk.Button(root, text="Submit Answer", command=app_instance.check_answer, width=20,
                                        height=2, font=("Arial", 12, "bold"))
    app_instance.submit_btn.pack(pady=30)

# result at the end of quiz
def create_quiz_result_frame(root, app_instance):
    clear_frame(root)
    tk.Button(root, text="Back", command=lambda: create_menu_frame(root, app_instance), width=10, height=2, font=("Arial", 12)).pack(anchor="nw", padx=10, pady=10)

    percent = int((app_instance.score / 5) * 100)
    msg = {
        0: "Better luck next time!",
        1: "Keep practicing!",
        2: "You're getting there!",
        3: "Good job!",
        4: "Excellent work!",
        5: "You are a genius!"
    }[app_instance.score]

    tk.Label(root, text="Quiz Complete!", font=("Arial", 20, "bold"), bg=root['bg']).pack(pady=20)
    tk.Label(root, text=f"Your Score: {app_instance.score}/5 ({percent}%)", font=("Arial", 16), bg=root['bg']).pack(pady=10)
    tk.Label(root, text=msg, font=("Arial", 14, "italic"), bg=root['bg']).pack(pady=10)

    if percent < 60:
        tk.Button(root, text="Retake Quiz", command=app_instance.start_quiz, width=20, height=2,
                  font=("Arial", 12)).pack(pady=15)

# show scores page
def create_scores_frame(root, app_instance, user_results, all_results):
    clear_frame(root)
    tk.Button(root, text="Back", command=lambda: create_menu_frame(root, app_instance), width=10, height=2, font=("Arial", 12)).pack(anchor="nw", padx=10, pady=10)
    tk.Label(root, text="Your Quiz History", font=("Arial", 20, "bold"), bg=root['bg']).pack(pady=15)

    if not user_results:
        tk.Label(root, text="No quiz attempts yet. Take a quiz to see your scores!", font=("Arial", 14), bg=root['bg']).pack(pady=20)
    else:
        scores = [r['score'] for r in user_results]

        tk.Label(root, text=f"Total Quizzes: {len(user_results)}", font=("Arial", 12), bg=root['bg']).pack(pady=2)
        tk.Label(root, text=f"Average Score: {sum(scores) / len(scores):.2f}/5", font=("Arial", 12), bg=root['bg']).pack(pady=2)
        tk.Label(root, text=f"Your Highest Score: {max(scores)}/5", font=("Arial", 12), bg=root['bg']).pack(pady=2)
        tk.Label(root, text=f"Your Lowest Score: {min(scores)}/5", font=("Arial", 12), bg=root['bg']).pack(pady=2)

        overall_highest_score = max([r['score'] for r in all_results]) if all_results else 0
        last_score = user_results[-1]['score']
        your_highest_score = max(scores)

        labels = ['Your Last Score', 'Your Highest Score', 'Overall Highest Score']
        values = [last_score, your_highest_score, overall_highest_score]
        colors = ['skyblue', 'lightcoral', 'lightgreen']

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.bar(labels, values, color=colors)
        ax.set_ylim(0, 5.5)
        ax.set_ylabel('Score (out of 5)')
        ax.set_title('Your Performance Overview vs. Overall')

        for i, v in enumerate(values):
            ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(pady=20)
        canvas.draw()