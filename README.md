# SanjAI

## Overview

SanjAI is your personal virtual tutor that helps you with all of your educational needs. Having trouble with homework questions? Want to learn something new? Need custom-made quizzes? SanjAI has your back. SanjAI has login, register and logout authentication with encrypted and hashed passwords to ensure security. SanjAI uses OpenAI's GPT 3-turbo API to answer and process all of your educational queries. Your prompt is sent directly to the API with engineered prompts that adhere to educational purposes. SanjAI also helps you stay on task with a built-in To-Do list feature where you can store your tasks in a list, sort them and mark them off. Unlock your hidden productivity with SanjAI.

## Features

### User Authentication

Registration: Users can create accounts with a unique username and password.

Login: Users can access the application using thier credentials.

### ChatBOT Tutoring

Prompt Submission/ Engineering: Prompts are received by the user and engineered to provide educational answers.

ChatBOT Logging: All successful prompts are logged for future reference.

### Multiple-Choice Quiz Generation

Quiz Prompt: A quiz is generated based on the prompt entered by the user.

User Interaction: Users can answer quiz questions, and the application provides feedback on correctness.

### To-Do list 

Task Addition: Users can add tasks to their ToDo list.

Task Deletion: Users can remove tasks from the ToDo list.

Sorting: Tasks in the ToDo list can be sorted by length or the number of characters.

### Session Management

User Sessions: User-specific data, such as To-Do lists and chatbot outputs, are managed using Flask session functionality.


## Getting Started

1) Install dependencies: pip install -r requirements.txt

2) Open Command Prompt: You can find it by searching "cmd" in the start menu.

3) Set environment variable in the current session: To set the environment variable in the current session, use the command below, replacing your-api-key-here with your actual API key:

***setx OPENAI_API_KEY "YOURKEYHERE"***

2) Run the application: python app.py

## Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Login
- Flask-Bcrypt
- OpenAI GPT-3 Python Library (Ensure you have API keys configured)
