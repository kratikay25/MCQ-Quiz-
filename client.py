import socket

from config import HOST, PORT
from protocol import send_message, receive_message


# -----------------------------
# Connect to Quiz Server
# -----------------------------

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:

    client.connect((HOST, PORT))

    print("=" * 55)
    print("       CLASSROOM MCQ QUIZ CLIENT")
    print("=" * 55)

    print("\nConnected to Quiz Server.")


    # -----------------------------
    # Student Registration
    # -----------------------------

    message = receive_message(client)

    if message == "ENTER_NAME":

        student_name = input(
            "\nEnter your name: "
        ).strip()

        while not student_name:

            print(
                "Name cannot be empty."
            )

            student_name = input(
                "Enter your name: "
            ).strip()

        send_message(
            client,
            student_name
        )


    # -----------------------------
    # Receive Assigned Set
    # -----------------------------

    message = receive_message(client)

    if message.startswith(
        "ASSIGNED_SET:"
    ):

        assigned_set = message.split(
            ":",
            1
        )[1]

        print(
            f"\nYou have been assigned: "
            f"{assigned_set}"
        )

        print(
            "\nQuiz is starting..."
        )

        print("=" * 55)


    # -----------------------------
    # Quiz Loop
    # -----------------------------

    while True:

        message = receive_message(
            client
        )

        if not message:
            break


        # Final Result

        if "Quiz Finished!" in message:

            print(
                "\n" + "=" * 55
            )

            print(message)

            print(
                "=" * 55
            )

            break


        # Display Question

        print(
            "\n" + message
        )


        # Get Valid Answer

        while True:

            answer = input(
                "\nEnter your answer "
                "(1-4): "
            ).strip()

            if answer in [
                "1",
                "2",
                "3",
                "4"
            ]:

                break

            print(
                "Invalid option. "
                "Please enter "
                "1, 2, 3 or 4."
            )


        # Send Answer

        send_message(
            client,
            answer
        )


        # Receive Result

        result = receive_message(
            client
        )

        print(
            "\nResult: "
            + result
        )

        print(
            "-" * 55
        )


except ConnectionRefusedError:

    print(
        "\nUnable to connect to the server."
    )

    print(
        "Please make sure the "
        "Quiz Server is running."
    )


except Exception as e:

    print(
        f"\nAn error occurred: {e}"
    )


finally:

    client.close()

    print(
        "\nConnection Closed."
    )