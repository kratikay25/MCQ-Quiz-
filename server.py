import socket
import threading
import random
import csv
import os
import json
from datetime import datetime

from config import HOST, PORT, MAX_CLIENTS
from protocol import send_message, receive_message
from questions import questions


# =====================================================
# CONFIGURATION
# =====================================================

QUESTIONS_PER_STUDENT = 5

RESULTS_FILE = "quiz_results.csv"
LIVE_STATUS_FILE = "live_status.csv"
CUSTOM_QUESTIONS_FILE = "custom_quiz.json"


# =====================================================
# SHARED DATA
# =====================================================

results = []

results_lock = threading.Lock()
live_status_lock = threading.Lock()

active_students = {}


# =====================================================
# SAVE COMPLETED RESULT
# =====================================================

def save_result_to_csv(result):

    file_exists = os.path.exists(
        RESULTS_FILE
    )

    with open(
        RESULTS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Student Name",
                "Quiz ID",
                "Score",
                "Percentage",
                "Status",
                "Submission Time"
            ])

        writer.writerow([
            result["name"],
            result["quiz_id"],
            result["score"],
            result["percentage"],
            result["status"],
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ])


# =====================================================
# UPDATE LIVE STATUS FILE
# =====================================================

def update_live_status_file():

    with live_status_lock:

        with open(
            LIVE_STATUS_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Student Name",
                "Quiz ID",
                "Progress",
                "Status",
                "Connected Time"
            ])

            for student in active_students.values():

                writer.writerow([
                    student["name"],
                    student["quiz_id"],
                    student["progress"],
                    student["status"],
                    student["connected_time"]
                ])


# =====================================================
# ADD ACTIVE STUDENT
# =====================================================

def add_active_student(
    quiz_id,
    student_name,
    total_questions
):

    with live_status_lock:

        active_students[quiz_id] = {

            "name":
                student_name,

            "quiz_id":
                quiz_id,

            "progress":
                f"0/{total_questions}",

            "status":
                "IN PROGRESS",

            "connected_time":
                datetime.now().strftime(
                    "%H:%M:%S"
                ),

            "total_questions":
                total_questions
        }

    update_live_status_file()


# =====================================================
# UPDATE STUDENT PROGRESS
# =====================================================

def update_student_progress(
    quiz_id,
    completed_questions
):

    with live_status_lock:

        if quiz_id in active_students:

            total_questions = (
                active_students[
                    quiz_id
                ][
                    "total_questions"
                ]
            )

            active_students[
                quiz_id
            ][
                "progress"
            ] = (

                f"{completed_questions}/"
                f"{total_questions}"
            )

    update_live_status_file()


# =====================================================
# MARK STUDENT COMPLETED
# =====================================================

def mark_student_completed(
    quiz_id
):

    with live_status_lock:

        if quiz_id in active_students:

            total_questions = (
                active_students[
                    quiz_id
                ][
                    "total_questions"
                ]
            )

            active_students[
                quiz_id
            ][
                "progress"
            ] = (

                f"{total_questions}/"
                f"{total_questions}"
            )

            active_students[
                quiz_id
            ][
                "status"
            ] = "COMPLETED"

    update_live_status_file()


# =====================================================
# GENERATE QUIZ
# =====================================================

def generate_quiz():

    # -------------------------------------------------
    # FIRST TRY PROFESSOR-CREATED QUIZ
    # -------------------------------------------------

    if os.path.exists(
        CUSTOM_QUESTIONS_FILE
    ):

        try:

            with open(
                CUSTOM_QUESTIONS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                custom_questions = json.load(
                    file
                )

            if (
                isinstance(
                    custom_questions,
                    list
                )
                and
                len(custom_questions) > 0
            ):

                print(
                    "\nProfessor-created quiz loaded."
                )

                print(
                    f"Questions: "
                    f"{len(custom_questions)}"
                )

                return (
                    custom_questions.copy(),
                    "Professor Quiz"
                )

        except Exception as e:

            print(
                "\nUnable to load "
                "professor-created quiz:"
            )

            print(
                e
            )

            print(
                "Using default question bank."
            )


    # -------------------------------------------------
    # FALLBACK TO RANDOM DEFAULT QUESTIONS
    # -------------------------------------------------

    number_of_questions = min(
        QUESTIONS_PER_STUDENT,
        len(questions)
    )

    random_quiz = random.sample(
        questions,
        number_of_questions
    )

    print(
        "\nNo professor-created quiz found."
    )

    print(
        "Using randomized default quiz."
    )

    return (
        random_quiz,
        "Random Quiz"
    )


# =====================================================
# SERVER SETUP
# =====================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (
        HOST,
        PORT
    )
)

server.listen(
    MAX_CLIENTS
)


# =====================================================
# SHOW PROFESSOR RESULTS
# =====================================================

def show_results():

    print(
        "\n"
        + "=" * 75
    )

    print(
        "                     "
        "PROFESSOR RESULTS DASHBOARD"
    )

    print(
        "=" * 75
    )

    print(
        f"{'Student':<20}"
        f"{'Score':<12}"
        f"{'Percentage':<15}"
        f"{'Status':<15}"
    )

    print(
        "-" * 75
    )

    with results_lock:

        for result in results:

            print(
                f"{result['name']:<20}"
                f"{result['score']:<12}"
                f"{result['percentage']:<15}"
                f"{result['status']:<15}"
            )

    print(
        "=" * 75
    )

    print(
        f"Completed Quizzes: "
        f"{len(results)}"
    )

    print(
        "=" * 75
    )


# =====================================================
# HANDLE STUDENT
# =====================================================

def handle_student(
    client_socket,
    address
):

    student_name = "Unknown"
    quiz_id = None

    try:

        print(
            f"\nNew connection from "
            f"{address[0]}:"
            f"{address[1]}"
        )


        # -------------------------------------------------
        # REQUEST STUDENT NAME
        # -------------------------------------------------

        send_message(
            client_socket,
            "ENTER_NAME"
        )

        student_name = receive_message(
            client_socket
        )

        if not student_name:

            return


        # -------------------------------------------------
        # GENERATE / LOAD QUIZ
        # -------------------------------------------------

        student_quiz, quiz_type = (
            generate_quiz()
        )

        total_questions = len(
            student_quiz
        )

        if total_questions == 0:

            send_message(
                client_socket,
                "Quiz Finished!\n\n"
                "No questions are currently available."
            )

            return


        # -------------------------------------------------
        # CREATE QUIZ ID
        # -------------------------------------------------

        quiz_id = (
            datetime.now()
            .strftime(
                "%H%M%S%f"
            )
        )


        print(
            f"\nStudent connected: "
            f"{student_name}"
        )

        print(
            f"Quiz Type: "
            f"{quiz_type}"
        )

        print(
            f"Questions: "
            f"{total_questions}"
        )

        print(
            f"Quiz ID: "
            f"{quiz_id}"
        )


        # -------------------------------------------------
        # ADD STUDENT TO LIVE DASHBOARD
        # -------------------------------------------------

        add_active_student(
            quiz_id,
            student_name,
            total_questions
        )


        # -------------------------------------------------
        # SEND QUIZ INFORMATION
        # -------------------------------------------------

        send_message(
            client_socket,

            f"ASSIGNED_SET:"
            f"{quiz_type} "
            f"{quiz_id[-4:]}"
        )


        score = 0


        # =================================================
        # SEND QUESTIONS
        # =================================================

        for number, question in enumerate(
            student_quiz,
            start=1
        ):

            question_text = (

                f"Question "
                f"{number}/"
                f"{total_questions}"
                f"\n\n"

                f"{question['question']}"
                f"\n\n"

                + "\n".join(
                    question[
                        "options"
                    ]
                )
            )


            send_message(
                client_socket,
                question_text
            )


            answer = receive_message(
                client_socket
            )


            if not answer:

                return


            # -------------------------------------------------
            # CHECK ANSWER
            # -------------------------------------------------

            if (
                str(answer)
                ==
                str(
                    question[
                        "answer"
                    ]
                )
            ):

                score += 1


            # -------------------------------------------------
            # UPDATE LIVE PROGRESS
            # -------------------------------------------------

            update_student_progress(
                quiz_id,
                number
            )


            # -------------------------------------------------
            # ACKNOWLEDGE ANSWER
            # -------------------------------------------------

            send_message(
                client_socket,
                "Answer submitted."
            )


        # =================================================
        # CALCULATE RESULT
        # =================================================

        percentage = round(

            (
                score
                /
                total_questions
            )

            * 100,

            2
        )


        # =================================================
        # CREATE RESULT
        # =================================================

        result_data = {

            "name":
                student_name,

            "quiz_id":
                quiz_id,

            "score":
                f"{score}/"
                f"{total_questions}",

            "percentage":
                f"{percentage}%",

            "status":
                "COMPLETED"
        }


        # -------------------------------------------------
        # STORE RESULT IN MEMORY
        # -------------------------------------------------

        with results_lock:

            results.append(
                result_data
            )


        # -------------------------------------------------
        # SAVE RESULT TO CSV
        # -------------------------------------------------

        save_result_to_csv(
            result_data
        )


        # -------------------------------------------------
        # UPDATE LIVE DASHBOARD
        # -------------------------------------------------

        mark_student_completed(
            quiz_id
        )


        # =================================================
        # SEND FINAL RESULT
        # =================================================

        final_result = (

            "Quiz Finished!"
            "\n\n"

            f"Student: "
            f"{student_name}"
            "\n"

            f"Quiz ID: "
            f"{quiz_id}"
            "\n"

            f"Score: "
            f"{score}/"
            f"{total_questions}"
            "\n"

            f"Percentage: "
            f"{percentage}%"
        )


        send_message(
            client_socket,
            final_result
        )


        # =================================================
        # TERMINAL OUTPUT
        # =================================================

        print(
            f"\nQuiz submitted by: "
            f"{student_name}"
        )

        print(
            f"Score: "
            f"{score}/"
            f"{total_questions}"
        )

        print(
            f"Result saved to: "
            f"{RESULTS_FILE}"
        )


        show_results()


    except Exception as e:

        print(
            f"\nError with student "
            f"{student_name}: "
            f"{e}"
        )


    finally:

        client_socket.close()

        print(
            f"\nConnection closed: "
            f"{student_name}"
        )


# =====================================================
# INITIALIZE LIVE STATUS FILE
# =====================================================

update_live_status_file()


# =====================================================
# START SERVER
# =====================================================

print(
    "=" * 70
)

print(
    "              "
    "CLASSROOM MCQ QUIZ SERVER"
)

print(
    "=" * 70
)

print(
    f"Server running on "
    f"{HOST}:{PORT}"
)

print(
    f"Default Questions in Bank: "
    f"{len(questions)}"
)

print(
    f"Default Questions Per Student: "
    f"{QUESTIONS_PER_STUDENT}"
)

print(
    f"Maximum Clients: "
    f"{MAX_CLIENTS}"
)

print(
    f"Results File: "
    f"{RESULTS_FILE}"
)

print(
    f"Live Status File: "
    f"{LIVE_STATUS_FILE}"
)

print(
    f"Custom Quiz File: "
    f"{CUSTOM_QUESTIONS_FILE}"
)

print(
    "\nWaiting for students "
    "to connect..."
)

print(
    "=" * 70
)


# =====================================================
# ACCEPT STUDENT CONNECTIONS
# =====================================================

try:

    while True:

        client_socket, address = (
            server.accept()
        )


        student_thread = threading.Thread(

            target=handle_student,

            args=(
                client_socket,
                address
            ),

            daemon=True
        )


        student_thread.start()


except KeyboardInterrupt:

    print(
        "\n\nQuiz Server Stopped."
    )


finally:

    server.close()