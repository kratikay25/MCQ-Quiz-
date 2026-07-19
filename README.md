### Classroom MCQ Quiz System

A multi-client classroom quiz application developed using Python, TCP socket programming, multithreading, and Tkinter. The system allows multiple students to participate in randomized MCQ quizzes while a professor manages the quiz server, monitors live student activity, creates questions, and views results through a graphical dashboard.

Project Overview

The Classroom MCQ Quiz System is designed to provide a simple network-based platform for conducting classroom quizzes.

The project follows a client-server architecture. A central quiz server manages student connections, generates randomized quizzes, evaluates answers, and stores results. Students access quizzes through a graphical client application, while the professor uses a separate dashboard to control the server and monitor quiz activity.

### Features

### Student Application

- Graphical student login interface
- Connection to the central quiz server
- Randomized quiz generation
- Unique Quiz ID for every attempt
- Multiple-choice question interface
- One-question-at-a-time navigation
- Automatic answer submission
- Automatic score calculation
- Final score and percentage display

 ### Professor Dashboard

- Start and stop the quiz server
- View server ONLINE/OFFLINE status
- Monitor live student activity
- View student quiz progress
- Track students currently in progress
- View completed quiz results
- Display total completed quizzes
- Calculate class average
- Display highest score
- Refresh dashboard data
- Open the results CSV file

### Quiz Creator

The Professor Quiz Creator allows professors to create quiz questions without manually editing the Python source code.

Each question contains:

- Question text
- Option 1
- Option 2
- Option 3
- Option 4
- Correct answer

Created questions can be saved and used by the quiz system.

## Technologies Used

- Python
- TCP Socket Programming
- Multithreading
- Tkinter
- CSV File Handling
- JSON File Handling
- Python Random Module

## System Architecture

The application follows a client-server architecture.

### Client

The student application acts as the client. It connects to the server, sends the student's information and answers, and receives quiz questions and final results.

### Server

The server is responsible for:

- Accepting student connections
- Managing multiple clients
- Generating randomized quizzes
- Sending questions to students
- Receiving student answers
- Checking answers
- Calculating scores
- Generating unique Quiz IDs
- Updating live student activity
- Saving completed results

### Professor Dashboard

The professor dashboard provides a graphical interface for managing and monitoring the entire quiz system.

The basic communication flow is:

Student Client
      |
      | TCP Connection
      |
Quiz Server
      |
      | Quiz Data and Results
      |
Professor Dashboard

## Project Workflow

1. The professor launches the Professor Quiz Dashboard.
2. The professor starts the quiz server.
3. The server begins listening for student connections.
4. A student opens the Student Quiz application.
5. The student enters their name and connects to the server.
6. The server generates a unique Quiz ID.
7. A randomized set of questions is assigned to the student.
8. Questions are displayed one at a time.
9. The student selects and submits answers.
10. Student progress is updated during the quiz.
11. The server checks the submitted answers.
12. The final score and percentage are calculated.
13. The result is saved to a CSV file.
14. The student receives the final result.
15. The professor can view the result from the dashboard.

## Randomized Quiz Generation

The server randomly selects questions from the available question bank.

For example:

- Questions in Question Bank: 10
- Questions Per Student: 5

The `random.sample()` function is used to select questions without repetition.

This allows different students to receive different combinations of questions.

## Multi-Client Support

The system supports multiple students connecting to the quiz server simultaneously.

Python multithreading is used to create a separate thread for every connected student.

This allows one student to complete their quiz independently while the server continues accepting and processing other student connections.

The maximum number of supported clients can be configured in the project settings.

## Live Student Monitoring

The professor dashboard provides a Live Student Activity section.

It displays:

- Student Name
- Quiz ID
- Quiz Progress
- Current Status
- Connected Time

Student status can include:

- IN PROGRESS
- COMPLETED

This allows the professor to monitor quiz activity during a classroom session.

## Result Management

After a student completes the quiz, the system automatically calculates the score and percentage.

Results are stored in:

`quiz_results.csv`

The result file contains:

- Student Name
- Quiz ID
- Score
- Percentage
- Status
- Submission Time

The professor can access these results directly from the dashboard.

## Project Structure

A typical project structure is:

MCQ_Socket_Project/
|
|-- server.py
|-- student_gui.py
|-- professor_gui.py
|-- questions.py
|-- protocol.py
|-- config.py
|-- quiz_results.csv
|-- live_status.csv
|-- custom_questions.json
|-- README.md

### File Description

#### server.py

Contains the main quiz server logic, including:

- Socket creation
- Client connection handling
- Multithreading
- Random quiz generation
- Answer evaluation
- Score calculation
- Result storage
- Live status updates

#### student_gui.py

Contains the graphical student application used to:

- Enter the student name
- Connect to the server
- Display quiz questions
- Select answers
- Submit answers
- Display final results

#### professor_gui.py

Contains the Professor Quiz Dashboard and Quiz Creator functionality.

It allows the professor to:

- Control the server
- Monitor student activity
- View quiz results
- Create new questions
- Access stored results

#### questions.py

Contains the default question bank used by the quiz server.

#### protocol.py

Handles message transmission between the client and server.

#### config.py

Contains common network configuration settings such as:

- Host address
- Port number
- Maximum number of clients

#### quiz_results.csv

Stores completed student quiz results.

#### live_status.csv

Stores current student quiz activity and progress.

#### custom_questions.json

Stores questions created through the Professor Quiz Creator.

## How to Run the Project

Make sure Python is installed on the system.

Open Terminal and navigate to the project directory:

```bash
cd ~/Downloads/Internship\ 2.0/MCQ_Socket_Project
