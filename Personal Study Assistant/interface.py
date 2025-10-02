import random
import requests
import html
from tkinter import *

TOPICS = {
    "General Knowledge": 9,
    "Books": 10,
    "Computers": 18,
    "Nature": 17,
    "History": 23,
    "Geography": 22,
    "Math": 19,
    "Animals": 27,
}

class QuizApp:
    def __init__(self):
        self.q_num = 0
        self.total_questions = 10
        self.score = {"correct": 0, "wrong": 0}
        self.time = 30

        self.root = Tk()
        self.root.title("Study Buddy")
        self.root.configure(bg="#FFF1E6")
        self.root.geometry("600x500")

        self.init_ui()

        self.root.mainloop()

    def init_ui(self):
        Label(self.root, text="Welcome!\nEnter your name and choose a topic:",
              font=("Arial", 18), bg="#FFF1E6", fg="#6E4F3A", wraplength=500).pack(pady=20)

        self.name_entry = Entry(self.root, font=("Arial", 18), justify="center")
        self.name_entry.pack(pady=10)

        self.topic_var = StringVar(value="Pick a topic")
        OptionMenu(self.root, self.topic_var, *TOPICS.keys()).pack()

        Button(self.root, text="Start", font=("Arial", 16), command=self.start_quiz).pack(pady=20)

        Button(self.root, text="See Previous Scores", command=self.show_scores, bg="#EFE2D0", fg="#4A403A").pack()

    def start_quiz(self):
        name = self.name_entry.get().strip()
        topic = self.topic_var.get()

        if topic not in TOPICS:
            return  # maybe show a warning later

        self.category = TOPICS[topic]

        with open("topics.txt", "w", encoding="utf-8") as f:
            f.write(name + "\n")

        self.clear_screen()
        self.show_question()

    def show_question(self):
        if self.q_num >= self.total_questions:
            self.end_quiz()
            return

        self.time_left = self.time
        self.selected = False

        self.clear_screen()

        try:
            r = requests.get("https://opentdb.com/api.php", params={
                "amount": 1, "category": self.category, "type": "multiple"
            })
            qdata = r.json().get("results", [])[0]
        except:
            self.show_question()
            return

        self.correct_answer = html.unescape(qdata['correct_answer'])
        options = [html.unescape(ans) for ans in qdata['incorrect_answers']]
        options.append(self.correct_answer)
        random.shuffle(options)

        self.q_num += 1

        Label(self.root, text=html.unescape(qdata['question']),
              wraplength=550, font=("Arial", 14), bg="#FFF1E6").pack(pady=15)

        self.answer_buttons = []
        for opt in options:
            btn = Button(self.root, text=opt, font=("Arial", 12), width=50,
                         command=lambda x=opt: self.check_answer(x))
            btn.pack(pady=4)
            self.answer_buttons.append(btn)

        self.feedback_label = Label(self.root, text="", bg="#FFF1E6", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

        self.timer_label = Label(self.root, text="", bg="#FFF1E6")
        self.timer_label.pack()
        self.update_timer()

    def check_answer(self, ans):
        if self.selected:
            return
        self.selected = True

        if ans == self.correct_answer:
            self.score["correct"] += 1
            self.feedback_label.config(text="Correct!", fg="green")
        else:
            self.score["wrong"] += 1
            self.feedback_label.config(text=f"Oops! Right answer was: {self.correct_answer}", fg="red")

        for b in self.answer_buttons:
            b.config(state=DISABLED)

        Button(self.root, text="Next", command=self.show_question).pack(pady=10)

    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {self.time_left}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif not self.selected:
            self.check_answer("")

    def end_quiz(self):
        self.clear_screen()
        Label(self.root, text=f"Done! Score: {self.score['correct']} right, {self.score['wrong']} wrong",
              font=("Arial", 16), bg="#FFF1E6").pack(pady=30)

        with open("quiz_results.txt", "a", encoding="utf-8") as f:
            f.write(f"Correct: {self.score['correct']}, Wrong: {self.score['wrong']}\n")

        Button(self.root, text="Restart", command=self.restart).pack(pady=20)

    def show_scores(self):
        self.clear_screen()
        try:
            with open("quiz_results.txt", "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            text = "No scores yet."

        Label(self.root, text="Previous Scores:\n" + text, font=("Arial", 12), bg="#FFF1E6", wraplength=550).pack(pady=20)
        Button(self.root, text="Back", command=self.restart).pack()

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    def restart(self):
        self.q_num = 0
        self.score = {"correct": 0, "wrong": 0}
        self.clear_screen()
        self.init_ui()

QuizApp()
