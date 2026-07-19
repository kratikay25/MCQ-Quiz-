import socket
import threading
import tkinter as tk
from tkinter import messagebox

from config import HOST, PORT
from protocol import send_message, receive_message


class StudentQuizApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Classroom MCQ Quiz")
        self.root.geometry("850x650")
        self.root.minsize(750, 600)

        # ==========================================
        # THEME
        # ==========================================

        self.BG = "#F4F6F8"
        self.CARD = "#FFFFFF"
        self.TEXT = "#1F2937"
        self.MUTED = "#6B7280"
        self.PRIMARY = "#2563EB"
        self.PRIMARY_ACTIVE = "#1D4ED8"
        self.SUCCESS = "#15803D"

        self.root.configure(bg=self.BG)

        # ==========================================
        # APPLICATION STATE
        # ==========================================

        self.client = None
        self.student_name = ""
        self.quiz_name = ""

        self.selected_answer = tk.StringVar(value="")

        # ==========================================
        # MAIN CONTAINER
        # ==========================================

        self.container = tk.Frame(
            self.root,
            bg=self.BG
        )

        self.container.pack(
            fill="both",
            expand=True
        )

        self.show_login_screen()


    # ==========================================
    # CLEAR CURRENT SCREEN
    # ==========================================

    def clear_screen(self):

        for widget in self.container.winfo_children():
            widget.destroy()


    # ==========================================
    # LOGIN SCREEN
    # ==========================================

    def show_login_screen(self):

        self.clear_screen()

        login_frame = tk.Frame(
            self.container,
            bg=self.CARD,
            padx=70,
            pady=60,
            highlightbackground="#D1D5DB",
            highlightthickness=1
        )

        login_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Title

        tk.Label(
            login_frame,
            text="CLASSROOM MCQ QUIZ",
            font=("Arial", 28, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            pady=(0, 15)
        )

        # Subtitle

        tk.Label(
            login_frame,
            text="Student Login",
            font=("Arial", 18, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            pady=10
        )

        # Instructions

        tk.Label(
            login_frame,
            text="Enter your name to begin the quiz",
            font=("Arial", 12),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            pady=(5, 15)
        )

        # Name Entry

        self.name_entry = tk.Entry(
            login_frame,
            font=("Arial", 16),
            width=30,
            justify="center",
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            relief="solid",
            bd=1
        )

        self.name_entry.pack(
            pady=15,
            ipady=10
        )

        self.name_entry.focus_set()

        # Connect Button

        self.connect_button = tk.Button(
            login_frame,
            text="Connect & Start Quiz",
            font=("Arial", 14, "bold"),
            width=24,
            bg=self.PRIMARY,
            fg="#FFFFFF",
            activebackground=self.PRIMARY_ACTIVE,
            activeforeground="#FFFFFF",
            command=self.start_connection
        )

        self.connect_button.pack(
            pady=20,
            ipady=8
        )

        # Status

        self.status_label = tk.Label(
            login_frame,
            text="",
            font=("Arial", 11),
            bg=self.CARD,
            fg=self.MUTED
        )

        self.status_label.pack(
            pady=5
        )

        # Press Enter to start

        self.root.bind(
            "<Return>",
            lambda event: self.start_connection()
        )


    # ==========================================
    # START CONNECTION
    # ==========================================

    def start_connection(self):

        self.student_name = self.name_entry.get().strip()

        if not self.student_name:

            messagebox.showwarning(
                "Missing Name",
                "Please enter your name."
            )

            return

        self.connect_button.config(
            state="disabled"
        )

        self.status_label.config(
            text="Connecting to quiz server..."
        )

        # Connect without freezing GUI

        threading.Thread(
            target=self.connect_to_server,
            daemon=True
        ).start()


    # ==========================================
    # CONNECT TO SERVER
    # ==========================================

    def connect_to_server(self):

        try:

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect(
                (HOST, PORT)
            )

            # Receive ENTER_NAME

            message = receive_message(
                self.client
            )

            if message != "ENTER_NAME":

                raise Exception(
                    "Unexpected response from server."
                )

            # Send student name

            send_message(
                self.client,
                self.student_name
            )

            # Receive assigned quiz

            assigned_message = receive_message(
                self.client
            )

            if not assigned_message:

                raise Exception(
                    "Server closed the connection."
                )

            if assigned_message.startswith(
                "ASSIGNED_SET:"
            ):

                self.quiz_name = assigned_message.split(
                    ":",
                    1
                )[1]

            else:

                self.quiz_name = "Random Quiz"

            # Open quiz screen safely

            self.root.after(
                0,
                self.show_quiz_screen
            )

        except ConnectionRefusedError:

            self.root.after(
                0,
                self.connection_error,
                (
                    "Unable to connect to the quiz server.\n\n"
                    "Please ask the professor to start the server."
                )
            )

        except Exception as e:

            self.root.after(
                0,
                self.connection_error,
                str(e)
            )


    # ==========================================
    # CONNECTION ERROR
    # ==========================================

    def connection_error(self, error):

        messagebox.showerror(
            "Connection Error",
            error
        )

        self.show_login_screen()


    # ==========================================
    # QUIZ SCREEN
    # ==========================================

    def show_quiz_screen(self):

        # Remove Enter binding from login

        self.root.unbind("<Return>")

        self.clear_screen()

        # ==========================================
        # HEADER
        # ==========================================

        header_frame = tk.Frame(
            self.container,
            bg=self.BG
        )

        header_frame.pack(
            fill="x",
            padx=50,
            pady=(30, 10)
        )

        tk.Label(
            header_frame,
            text="CLASSROOM MCQ QUIZ",
            font=("Arial", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT
        ).pack()

        tk.Label(
            header_frame,
            text=(
                f"Student: {self.student_name}"
                f"     |     "
                f"{self.quiz_name}"
            ),
            font=("Arial", 12),
            bg=self.BG,
            fg=self.MUTED
        ).pack(
            pady=10
        )

        # ==========================================
        # QUIZ CARD
        # ==========================================

        self.quiz_frame = tk.Frame(
            self.container,
            bg=self.CARD,
            highlightbackground="#D1D5DB",
            highlightthickness=1
        )

        self.quiz_frame.pack(
            fill="both",
            expand=True,
            padx=70,
            pady=(10, 40)
        )

        # ==========================================
        # QUESTION
        # ==========================================

        self.question_label = tk.Label(
            self.quiz_frame,
            text="Loading your first question...",
            font=("Arial", 17, "bold"),
            bg=self.CARD,
            fg=self.TEXT,
            wraplength=650,
            justify="left",
            anchor="w"
        )

        self.question_label.pack(
            fill="x",
            padx=45,
            pady=(40, 25)
        )

        # ==========================================
        # OPTIONS
        # ==========================================

        self.options_frame = tk.Frame(
            self.quiz_frame,
            bg=self.CARD
        )

        self.options_frame.pack(
            fill="x",
            padx=45,
            pady=10
        )

        # ==========================================
        # STATUS
        # ==========================================

        self.status_text = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 11),
            bg=self.CARD,
            fg=self.MUTED
        )

        self.status_text.pack(
            pady=10
        )

        # ==========================================
        # SUBMIT BUTTON
        # ==========================================

        self.submit_button = tk.Button(
            self.quiz_frame,
            text="Submit Answer",
            font=("Arial", 14, "bold"),
            width=20,
            bg=self.PRIMARY,
            fg="#FFFFFF",
            activebackground=self.PRIMARY_ACTIVE,
            activeforeground="#FFFFFF",
            state="disabled",
            command=self.submit_answer
        )

        self.submit_button.pack(
            pady=(15, 35),
            ipady=8
        )

        # Receive first question

        threading.Thread(
            target=self.receive_first_question,
            daemon=True
        ).start()


    # ==========================================
    # RECEIVE FIRST QUESTION
    # ==========================================

    def receive_first_question(self):

        try:

            message = receive_message(
                self.client
            )

            if not message:

                raise Exception(
                    "Connection to the server was closed."
                )

            if "Quiz Finished!" in message:

                self.root.after(
                    0,
                    self.show_result,
                    message
                )

                return

            self.root.after(
                0,
                self.display_question,
                message
            )

        except Exception as e:

            self.root.after(
                0,
                self.show_network_error,
                str(e)
            )


    # ==========================================
    # DISPLAY QUESTION
    # ==========================================

    def display_question(self, message):

        # Clear previous selection

        self.selected_answer.set("")

        self.status_text.config(
            text=""
        )

        # Remove previous options

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Split server message

        lines = message.split("\n")

        question_lines = []
        options = []

        for line in lines:

            stripped = line.strip()

            # Detect options 1. 2. 3. 4.

            if (
                len(stripped) >= 2
                and stripped[0] in "1234"
                and stripped[1] == "."
            ):

                options.append(
                    stripped
                )

            elif stripped:

                question_lines.append(
                    stripped
                )

        # Build question text

        question_text = "\n\n".join(
            question_lines
        )

        self.question_label.config(
            text=question_text
        )

        # Create answer buttons

        for option in options:

            radio = tk.Radiobutton(
                self.options_frame,
                text=option,
                variable=self.selected_answer,
                value=option[0],
                font=("Arial", 14),
                bg=self.CARD,
                fg=self.TEXT,
                activebackground=self.CARD,
                activeforeground=self.TEXT,
                selectcolor="#E5E7EB",
                anchor="w",
                justify="left",
                padx=15,
                pady=10,
                command=self.enable_submit
            )

            radio.pack(
                fill="x",
                pady=4
            )

        # Disable until answer selected

        self.submit_button.config(
            state="disabled"
        )


    # ==========================================
    # ENABLE SUBMIT
    # ==========================================

    def enable_submit(self):

        self.submit_button.config(
            state="normal"
        )


    # ==========================================
    # SUBMIT ANSWER
    # ==========================================

    def submit_answer(self):

        answer = self.selected_answer.get()

        if not answer:

            messagebox.showwarning(
                "Select Answer",
                "Please select an answer."
            )

            return

        # Prevent double submission

        self.submit_button.config(
            state="disabled"
        )

        self.status_text.config(
            text="Submitting answer..."
        )

        # Send answer in background

        threading.Thread(
            target=self.send_answer,
            args=(answer,),
            daemon=True
        ).start()


    # ==========================================
    # SEND ANSWER AND RECEIVE NEXT QUESTION
    # ==========================================

    def send_answer(self, answer):

        try:

            # Send selected answer

            send_message(
                self.client,
                answer
            )

            # Receive acknowledgement:
            # "Answer submitted."

            acknowledgement = receive_message(
                self.client
            )

            if not acknowledgement:

                raise Exception(
                    "Server closed the connection."
                )

            # Show loading screen

            self.root.after(
                0,
                self.show_loading
            )

            # Receive next question OR final result

            next_message = receive_message(
                self.client
            )

            if not next_message:

                raise Exception(
                    "Server closed the connection."
                )

            # Quiz completed

            if "Quiz Finished!" in next_message:

                self.root.after(
                    0,
                    self.show_result,
                    next_message
                )

            # Next question

            else:

                self.root.after(
                    0,
                    self.display_question,
                    next_message
                )

        except Exception as e:

            self.root.after(
                0,
                self.show_network_error,
                str(e)
            )


    # ==========================================
    # SHOW LOADING
    # ==========================================

    def show_loading(self):

        self.question_label.config(
            text="Answer submitted."
        )

        self.status_text.config(
            text="Loading next question..."
        )

        # Remove old answer options

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.submit_button.config(
            state="disabled"
        )


    # ==========================================
    # NETWORK ERROR
    # ==========================================

    def show_network_error(self, error):

        messagebox.showerror(
            "Connection Error",
            error
        )


    # ==========================================
    # FINAL RESULT SCREEN
    # ==========================================

    def show_result(self, result):

        self.clear_screen()

        result_frame = tk.Frame(
            self.container,
            bg=self.CARD,
            padx=70,
            pady=50,
            highlightbackground="#D1D5DB",
            highlightthickness=1
        )

        result_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # Title

        tk.Label(
            result_frame,
            text="QUIZ COMPLETED",
            font=("Arial", 28, "bold"),
            bg=self.CARD,
            fg=self.SUCCESS
        ).pack(
            pady=(0, 20)
        )

        # Confirmation

        tk.Label(
            result_frame,
            text=(
                "Your answers have been "
                "submitted successfully."
            ),
            font=("Arial", 14),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(
            pady=10
        )

        # Result information

        tk.Label(
            result_frame,
            text=result,
            font=("Arial", 16),
            bg=self.CARD,
            fg=self.TEXT,
            justify="left"
        ).pack(
            pady=30
        )

        # Close button

        tk.Button(
            result_frame,
            text="Close",
            font=("Arial", 14, "bold"),
            width=15,
            bg=self.PRIMARY,
            fg="#FFFFFF",
            activebackground=self.PRIMARY_ACTIVE,
            activeforeground="#FFFFFF",
            command=self.close_application
        ).pack(
            pady=20,
            ipady=7
        )


    # ==========================================
    # CLOSE APPLICATION
    # ==========================================

    def close_application(self):

        try:

            if self.client:
                self.client.close()

        except Exception:
            pass

        self.root.destroy()


# ==============================================
# START APPLICATION
# ==============================================

if __name__ == "__main__":

    root = tk.Tk()

    app = StudentQuizApp(
        root
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        app.close_application
    )

    root.mainloop()