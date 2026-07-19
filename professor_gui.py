import csv
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

RESULTS_FILE = "quiz_results.csv"
LIVE_STATUS_FILE = "live_status.csv"
CUSTOM_QUESTIONS_FILE = "custom_questions.json"


class ProfessorDashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("Professor Quiz Dashboard")
        self.root.geometry("1200x820")
        self.root.minsize(1000, 700)

        self.server_process = None
        self.created_questions = []

        # Theme
        self.BG = "#F4F6F8"
        self.CARD = "#FFFFFF"
        self.TEXT = "#1F2937"
        self.MUTED = "#6B7280"
        self.GREEN = "#16A34A"
        self.RED = "#DC2626"
        self.BLUE = "#2563EB"

        self.root.configure(bg=self.BG)

        self.build_interface()
        self.load_all_data()
        self.auto_refresh()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )


    # ==================================================
    # BUILD INTERFACE
    # ==================================================

    def build_interface(self):

        # ------------------------------
        # HEADER
        # ------------------------------

        header = tk.Frame(
            self.root,
            bg=self.BG
        )

        header.pack(
            fill="x",
            padx=40,
            pady=(25, 10)
        )

        tk.Label(
            header,
            text="PROFESSOR QUIZ DASHBOARD",
            font=("Arial", 26, "bold"),
            bg=self.BG,
            fg=self.TEXT
        ).pack()

        tk.Label(
            header,
            text="Live Classroom Quiz Management & Results",
            font=("Arial", 13),
            bg=self.BG,
            fg=self.MUTED
        ).pack(pady=5)


        # ------------------------------
        # STATISTICS
        # ------------------------------

        stats_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        stats_frame.pack(
            fill="x",
            padx=40,
            pady=10
        )

        self.completed_label = self.create_stat_card(
            stats_frame,
            "Completed Quizzes"
        )

        self.active_label = self.create_stat_card(
            stats_frame,
            "Students In Progress"
        )

        self.average_label = self.create_stat_card(
            stats_frame,
            "Class Average"
        )

        self.highest_label = self.create_stat_card(
            stats_frame,
            "Highest Score"
        )


        # ------------------------------
        # SERVER STATUS
        # ------------------------------

        status_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        status_frame.pack(
            pady=(5, 10)
        )

        tk.Label(
            status_frame,
            text="Quiz Server:",
            font=("Arial", 12, "bold"),
            bg=self.BG,
            fg=self.TEXT
        ).pack(
            side="left"
        )

        self.server_status = tk.Label(
            status_frame,
            text="● OFFLINE",
            font=("Arial", 12, "bold"),
            bg=self.BG,
            fg=self.RED
        )

        self.server_status.pack(
            side="left",
            padx=10
        )


        # ==================================================
        # LIVE STUDENTS
        # ==================================================

        live_section = tk.Frame(
            self.root,
            bg=self.CARD
        )

        live_section.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=(5, 10)
        )

        tk.Label(
            live_section,
            text="LIVE STUDENT ACTIVITY",
            font=("Arial", 15, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        live_columns = (
            "student",
            "quiz_id",
            "progress",
            "status",
            "connected"
        )

        self.live_table = ttk.Treeview(
            live_section,
            columns=live_columns,
            show="headings",
            height=5
        )

        live_headings = {
            "student": "Student",
            "quiz_id": "Quiz ID",
            "progress": "Progress",
            "status": "Status",
            "connected": "Connected Time"
        }

        for column, heading in live_headings.items():

            self.live_table.heading(
                column,
                text=heading
            )

        self.live_table.column(
            "student",
            width=180
        )

        self.live_table.column(
            "quiz_id",
            width=200
        )

        self.live_table.column(
            "progress",
            width=120,
            anchor="center"
        )

        self.live_table.column(
            "status",
            width=150,
            anchor="center"
        )

        self.live_table.column(
            "connected",
            width=150,
            anchor="center"
        )

        self.live_table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )


        # ==================================================
        # COMPLETED RESULTS
        # ==================================================

        results_section = tk.Frame(
            self.root,
            bg=self.CARD
        )

        results_section.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=(10, 15)
        )

        tk.Label(
            results_section,
            text="COMPLETED QUIZ RESULTS",
            font=("Arial", 15, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        table_frame = tk.Frame(
            results_section,
            bg=self.CARD
        )

        table_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "student",
            "quiz_id",
            "score",
            "percentage",
            "status",
            "time"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=6
        )

        headings = {
            "student": "Student",
            "quiz_id": "Quiz ID",
            "score": "Score",
            "percentage": "Percentage",
            "status": "Status",
            "time": "Submission Time"
        }

        for column, heading in headings.items():

            self.table.heading(
                column,
                text=heading
            )

        self.table.column(
            "student",
            width=140
        )

        self.table.column(
            "quiz_id",
            width=160
        )

        self.table.column(
            "score",
            width=90,
            anchor="center"
        )

        self.table.column(
            "percentage",
            width=110,
            anchor="center"
        )

        self.table.column(
            "status",
            width=110,
            anchor="center"
        )

        self.table.column(
            "time",
            width=170
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 0),
            pady=(0, 15)
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 15),
            pady=(0, 15)
        )


        # ==================================================
        # BUTTONS
        # ==================================================

        button_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        button_frame.pack(
            pady=(0, 20)
        )

        self.server_button = tk.Button(
            button_frame,
            text="Start Quiz Server",
            font=("Arial", 12, "bold"),
            width=17,
            command=self.toggle_server
        )

        self.server_button.pack(
            side="left",
            padx=6,
            ipady=7
        )

        tk.Button(
            button_frame,
            text="Create Quiz",
            font=("Arial", 12, "bold"),
            width=15,
            bg=self.BLUE,
            fg="white",
            command=self.open_quiz_creator
        ).pack(
            side="left",
            padx=6,
            ipady=7
        )

        tk.Button(
            button_frame,
            text="Refresh Dashboard",
            font=("Arial", 12, "bold"),
            width=17,
            command=self.load_all_data
        ).pack(
            side="left",
            padx=6,
            ipady=7
        )

        tk.Button(
            button_frame,
            text="Open Results CSV",
            font=("Arial", 12),
            width=16,
            command=self.open_results
        ).pack(
            side="left",
            padx=6,
            ipady=7
        )


    # ==================================================
    # CREATE STAT CARD
    # ==================================================

    def create_stat_card(
        self,
        parent,
        title
    ):

        card = tk.Frame(
            parent,
            bg=self.CARD,
            padx=25,
            pady=15
        )

        card.pack(
            side="left",
            expand=True,
            fill="x",
            padx=7
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 11),
            bg=self.CARD,
            fg=self.MUTED
        ).pack()

        value_label = tk.Label(
            card,
            text="0",
            font=("Arial", 25, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        )

        value_label.pack()

        return value_label


    # ==================================================
    # QUIZ CREATOR
    # ==================================================

    def open_quiz_creator(self):

        self.created_questions = []

        self.creator = tk.Toplevel(
            self.root
        )

        self.creator.title(
            "Professor Quiz Creator"
        )

        self.creator.geometry(
            "900x850"
        )

        self.creator.minsize(
           800,
           750
        )

        self.creator.configure(
            bg=self.BG
        )

        self.creator.grab_set()


        # Header

        tk.Label(
            self.creator,
            text="CREATE CLASSROOM QUIZ",
            font=("Arial", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            self.creator,
            text="Create questions without editing Python code",
            font=("Arial", 12),
            bg=self.BG,
            fg=self.MUTED
        ).pack(
            pady=(0, 15)
        )


        # Main form

        form = tk.Frame(
         self.creator,
         bg=self.CARD,
         padx=40,
         pady=15
       )
        form.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=15
        )


        # Question

        tk.Label(
            form,
            text="Question",
            font=("Arial", 12, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            anchor="w"
        )

        self.question_entry = tk.Text(
            form,
            height=3,
            font=("Arial", 13),
            wrap="word"
        )

        self.question_entry.pack(
            fill="x",
            pady=(5, 15)
        )


        # Options

        self.option_entries = []

        for number in range(
            1,
            5
        ):

            tk.Label(
                form,
                text=f"Option {number}",
                font=("Arial", 11, "bold"),
                bg=self.CARD,
                fg=self.TEXT
            ).pack(
                anchor="w"
            )

            entry = tk.Entry(
                form,
                font=("Arial", 12)
            )

            entry.pack(
                fill="x",
                pady=(4, 10),
                ipady=5
            )

            self.option_entries.append(
                entry
            )


        # Correct answer

        answer_frame = tk.Frame(
            form,
            bg=self.CARD
        )

        answer_frame.pack(
            fill="x",
            pady=10
        )

        tk.Label(
            answer_frame,
            text="Correct Answer:",
            font=("Arial", 12, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            side="left"
        )

        self.correct_answer = tk.StringVar(
            value="1"
        )

        answer_menu = ttk.Combobox(
            answer_frame,
            textvariable=self.correct_answer,
            values=[
                "1",
                "2",
                "3",
                "4"
            ],
            width=8,
            state="readonly"
        )

        answer_menu.pack(
            side="left",
            padx=15
        )


        # Question counter

        self.question_count_label = tk.Label(
            form,
            text="Questions Added: 0",
            font=("Arial", 12, "bold"),
            bg=self.CARD,
            fg=self.BLUE
        )

        self.question_count_label.pack(
            pady=10
        )


        # Creator buttons

        creator_buttons = tk.Frame(
            form,
            bg=self.CARD
        )

        creator_buttons.pack(
            pady=15
        )

        tk.Button(
            creator_buttons,
            text="Add Question",
            font=("Arial", 12, "bold"),
            width=15,
            bg=self.BLUE,
            fg="white",
            command=self.add_question
        ).pack(
            side="left",
            padx=8,
            ipady=6
        )

        tk.Button(
            creator_buttons,
            text="Save Quiz",
            font=("Arial", 12, "bold"),
            width=15,
            bg=self.GREEN,
            fg="white",
            command=self.save_custom_quiz
        ).pack(
            side="left",
            padx=8,
            ipady=6
        )

        tk.Button(
            creator_buttons,
            text="Close",
            font=("Arial", 12),
            width=12,
            command=self.creator.destroy
        ).pack(
            side="left",
            padx=8,
            ipady=6
        )


    # ==================================================
    # ADD QUESTION
    # ==================================================

    def add_question(self):

        question = (
            self.question_entry
            .get(
                "1.0",
                "end"
            )
            .strip()
        )

        options = []

        for entry in self.option_entries:

            option = (
                entry
                .get()
                .strip()
            )

            options.append(
                option
            )


        if not question:

            messagebox.showwarning(
                "Missing Question",
                "Please enter a question."
            )

            return


        if any(
            not option
            for option in options
        ):

            messagebox.showwarning(
                "Missing Options",
                "Please enter all four answer options."
            )

            return


        formatted_options = [

            f"1. {options[0]}",

            f"2. {options[1]}",

            f"3. {options[2]}",

            f"4. {options[3]}"
        ]


        question_data = {

            "question":
                question,

            "options":
                formatted_options,

            "answer":
                self.correct_answer.get()
        }


        self.created_questions.append(
            question_data
        )


        self.question_count_label.config(
            text=(
                "Questions Added: "
                f"{len(self.created_questions)}"
            )
        )


        # Clear form

        self.question_entry.delete(
            "1.0",
            "end"
        )

        for entry in self.option_entries:

            entry.delete(
                0,
                "end"
            )


        self.correct_answer.set(
            "1"
        )


        self.question_entry.focus_set()


        messagebox.showinfo(
            "Question Added",
            (
                "Question added successfully.\n\n"
                f"Total questions: "
                f"{len(self.created_questions)}"
            )
        )


    # ==================================================
    # SAVE CUSTOM QUIZ
    # ==================================================

    def save_custom_quiz(self):

        if not self.created_questions:

            messagebox.showwarning(
                "No Questions",
                (
                    "Please add at least one "
                    "question before saving."
                )
            )

            return


        try:

            with open(
                CUSTOM_QUESTIONS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.created_questions,
                    file,
                    indent=4,
                    ensure_ascii=False
                )


            messagebox.showinfo(
                "Quiz Saved",
                (
                    "Quiz saved successfully!\n\n"
                    f"Questions: "
                    f"{len(self.created_questions)}\n\n"
                    f"Saved to: "
                    f"{CUSTOM_QUESTIONS_FILE}"
                )
            )


        except Exception as e:

            messagebox.showerror(
                "Save Error",
                (
                    "Unable to save quiz:\n"
                    f"{e}"
                )
            )


    # ==================================================
    # LOAD EVERYTHING
    # ==================================================

    def load_all_data(self):

        self.load_live_status()
        self.load_results()


    # ==================================================
    # LOAD LIVE STUDENT STATUS
    # ==================================================

    def load_live_status(self):

        for row in self.live_table.get_children():

            self.live_table.delete(
                row
            )


        active_count = 0


        if not os.path.exists(
            LIVE_STATUS_FILE
        ):

            self.active_label.config(
                text="0"
            )

            return


        try:

            with open(
                LIVE_STATUS_FILE,
                "r",
                newline=""
            ) as file:

                reader = csv.DictReader(
                    file
                )


                for row in reader:

                    status = row.get(
                        "Status",
                        ""
                    )


                    if status == "IN PROGRESS":

                        active_count += 1


                    self.live_table.insert(
                        "",
                        "end",
                        values=(

                            row.get(
                                "Student Name",
                                ""
                            ),

                            row.get(
                                "Quiz ID",
                                ""
                            ),

                            row.get(
                                "Progress",
                                ""
                            ),

                            status,

                            row.get(
                                "Connected Time",
                                ""
                            )
                        )
                    )


        except Exception as e:

            print(
                "Live status read error:",
                e
            )


        self.active_label.config(
            text=str(
                active_count
            )
        )


    # ==================================================
    # LOAD COMPLETED RESULTS
    # ==================================================

    def load_results(self):

        for row in self.table.get_children():

            self.table.delete(
                row
            )


        if not os.path.exists(
            RESULTS_FILE
        ):

            self.completed_label.config(
                text="0"
            )

            self.average_label.config(
                text="0%"
            )

            self.highest_label.config(
                text="0%"
            )

            return


        results = []


        try:

            with open(
                RESULTS_FILE,
                "r",
                newline=""
            ) as file:

                reader = csv.DictReader(
                    file
                )


                for row in reader:

                    results.append(
                        row
                    )


                    self.table.insert(
                        "",
                        "end",
                        values=(

                            row.get(
                                "Student Name",
                                ""
                            ),

                            row.get(
                                "Quiz ID",
                                ""
                            ),

                            row.get(
                                "Score",
                                ""
                            ),

                            row.get(
                                "Percentage",
                                ""
                            ),

                            row.get(
                                "Status",
                                ""
                            ),

                            row.get(
                                "Submission Time",
                                ""
                            )
                        )
                    )


        except Exception as e:

            print(
                "Results read error:",
                e
            )

            return


        percentages = []


        for result in results:

            try:

                percentage = float(

                    result.get(
                        "Percentage",
                        "0"
                    ).replace(
                        "%",
                        ""
                    )
                )


                percentages.append(
                    percentage
                )


            except ValueError:

                pass


        completed = len(
            results
        )


        if percentages:

            average = round(

                sum(
                    percentages
                )

                /

                len(
                    percentages
                ),

                1
            )


            highest = max(
                percentages
            )


        else:

            average = 0
            highest = 0


        self.completed_label.config(
            text=str(
                completed
            )
        )


        self.average_label.config(
            text=f"{average}%"
        )


        self.highest_label.config(
            text=f"{highest}%"
        )


    # ==================================================
    # SERVER CONTROL
    # ==================================================

    def toggle_server(self):

        if (

            self.server_process
            is None

            or

            self.server_process.poll()
            is not None

        ):

            self.start_server()


        else:

            self.stop_server()


    def start_server(self):

        try:

            self.server_process = (
                subprocess.Popen(
                    [
                        sys.executable,
                        "server.py"
                    ]
                )
            )


            self.root.after(
                700,
                self.check_server_started
            )


        except Exception as e:

            messagebox.showerror(
                "Server Error",
                f"Unable to start server:\n{e}"
            )


    def check_server_started(self):

        if (

            self.server_process

            and

            self.server_process.poll()
            is None

        ):

            self.server_button.config(
                text="Stop Quiz Server"
            )


            self.server_status.config(
                text="● ONLINE",
                fg=self.GREEN
            )


        else:

            self.server_process = None


            messagebox.showerror(

                "Server Error",

                "The server could not start.\n\n"
                "Another server may already be "
                "running on port 5000."
            )


    def stop_server(self):

        if self.server_process:

            self.server_process.terminate()


            try:

                self.server_process.wait(
                    timeout=3
                )


            except subprocess.TimeoutExpired:

                self.server_process.kill()


            self.server_process = None


        self.server_button.config(
            text="Start Quiz Server"
        )


        self.server_status.config(
            text="● OFFLINE",
            fg=self.RED
        )


    # ==================================================
    # OPEN RESULTS
    # ==================================================

    def open_results(self):

        if not os.path.exists(
            RESULTS_FILE
        ):

            messagebox.showwarning(
                "No Results",
                "No quiz results are available yet."
            )

            return


        try:

            if sys.platform == "darwin":

                subprocess.Popen(
                    [
                        "open",
                        RESULTS_FILE
                    ]
                )


            elif os.name == "nt":

                os.startfile(
                    RESULTS_FILE
                )


            else:

                subprocess.Popen(
                    [
                        "xdg-open",
                        RESULTS_FILE
                    ]
                )


        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Unable to open results:\n{e}"
            )


    # ==================================================
    # AUTO REFRESH
    # ==================================================

    def auto_refresh(self):

        self.load_all_data()


        self.root.after(
            2000,
            self.auto_refresh
        )


    # ==================================================
    # CLOSE APPLICATION
    # ==================================================

    def close_application(self):

        if (

            self.server_process

            and

            self.server_process.poll()
            is None

        ):

            self.server_process.terminate()


        self.root.destroy()


# ======================================================
# START APPLICATION
# ======================================================

if __name__ == "__main__":

    root = tk.Tk()


    app = ProfessorDashboard(
        root
    )


    root.mainloop()