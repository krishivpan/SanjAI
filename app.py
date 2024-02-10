from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from openai import OpenAI

# Flask miscellaneous
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'ICS4U'
SQLALCHEMY_TRACK_MODIFICATIONS = False

login_manager = LoginManager()  # class that handles log-in authentication
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # obtains a user based on their user id from the database

"""User Class"""

# Create a user class that stores the username and password and creates a unique id
class User(db.Model, UserMixin):
    """Manages the user's unique id and password"""
    id = db.Column(db.Integer, primary_key=True)  # specifications of a user's ID within the databse
    username = db.Column(db.String(20), nullable=False, unique=True)  # specifications of a user's name within the databse
    password = db.Column(db.String(80), nullable=False)  # specifications of a user's password within the databse

    def __init__(self, username, password):
        """Instance variables for username and password"""
        self.username = username
        self.password = password

    @staticmethod
    def search_user(query):
        """Finds user based on your query"""
        # Implement a search functionality based on the query
        return User.query.filter(User.username.ilike(f'%{query}%')).all()
    
    def __str__(self):
        """Returns the user's id and name"""
        return f"User ID: {self.id}, Username: {self.username}"

    def __eq__(self, other):
        """Compares 2 users' IDs"""
        if isinstance(other, User):
            return self.id == other.id and self.username == other.username
        return False
    

"""Form Classes"""


# Create the validation for the registration form
class RegisterForm(FlaskForm):
    """This class manages the specifications and restrictions for registration of a user"""
    def __init__(self):
        """Inherites user detials from User class"""
        super().__init__()

    # Creates a string field for the usename, with max and minimum length
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    # Creates a string field for the password, with max and minimum length
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")  # creates a submit field to sumbit username and password

    def validate_username(self, username):
        """Checks if a user already exists"""
        existing_user_username = User.query.filter_by(username=username.data).first()  # check if the username already exists in the database
        
        # If there an existing user, deny the creation of the account.
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")


class PromptForm(FlaskForm):
    """Handles the prompt field"""
    def __init__(self):
        super().__init__()

    # Creates a string field for the prompt with a minimum length of 5 to account for unprocessable prompts
    prompt = StringField(validators=[InputRequired(), Length(
        min=5)], render_kw={"placeholder": "What do you want to learn about?"})

    submit = SubmitField("Submit")  # submit field to sumbit the prompt


class LoginForm(FlaskForm):
    """Creates a form for the login of a user"""

    # Creates a string field for the username
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    # Creates a password field for the password
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")  # sumbit field to submit username and password


class ToDoForm(FlaskForm):
    """Creates a Form for the TO-DO list"""
    content = StringField(validators=[InputRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Task"})  # string field to input task
    submit = SubmitField("Add Task")  # submit field to submit task


"""Tutor Classes"""


class Tutor:
    """Creates logs if the prompt was successful"""
    def generate_output(self, prompt):
        """If subclasses are have not implemented an output"""
        raise NotImplementedError("Subclasses must implement generate_output method.")

    @staticmethod
    def log_info(message):
        """Returns a log message"""
        # Static method for logging information
        return f"Log: {message}"


class ChatTutor(Tutor):
    """Creates a Tutor ChatBot to help with questions"""
    def __init__(self):
        super(Tutor).__init__()

    def generate_output(self, prompt):
        """Generates an output based on the user prompt"""
        client = OpenAI()  # create the OpenAI client

        # Use OpenAI to generate an output based on the prompt
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
            ]
        )

        print(Tutor.log_info("Prompt has successfully been logged"))  # logs a successful prompt

        return completion.choices[0].message.content  # return the generated output


class QuizTutor(Tutor):
    """Creates a multiple choice quiz based on the prompt provided"""
    def __init__(self):
        super(Tutor).__init__()

    def generate_quiz(self, prompt):
        # Prompt engineer a prompt that will force the AI to generate a quiz with the specifications provided
        quiz_prompt = "create a unique multiple choice question with 4 options with the answer on the last line and 8 lines, on the following topic:" + prompt

        client = OpenAI()  # create the OpenAI client
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": quiz_prompt},
            ]
        )

        quiz_content = completion.choices[0].message.content  # store the generated prompt 
        return quiz_content  # return prompt


"""Route to Dashboard"""


class DashboardRoute:
    """Routes and processes form data for the dashboard."""

    @classmethod
    def process_form(cls, form):
        """Process form data when submitted."""
        if form.validate_on_submit():
            # Instantiate ChatTutor and generate output based on form prompt
            tutor = ChatTutor()
            output = tutor.generate_output(form.prompt.data)
            session['output'] = output

    @classmethod
    def render_template(cls, form):
        """Render the dashboard template."""
        return render_template('dashboard.html', form=form, variable=session.get('output', ''))
    

"""ToDo List Handler"""


class ToDoHandler:
    """Handles ToDo list operations and session management."""

    def __init__(self):
        """Initialize ToDoHandler with tasks from the session."""
        self.__todos = session.get('todos', [])

    def __update_session(self):
        """Update the session with the current list of tasks."""
        session['todos'] = self.__todos
        session.modified = True

    def __add_task(self, task):
        """Add a task to the ToDo list."""
        if task:
            self.__todos.append(task)
            self.__update_session()

    def __delete_task(self, index):
        """Delete a task from the ToDo list by index."""
        if 0 <= index < len(self.__todos):
            del self.__todos[index]
            self.__update_session()

    def __insertion_sort(self, key_function):
        """Sort tasks using the insertion sort algorithm based on the given key function."""
        for i in range(1, len(self.__todos)):
            current_task = self.__todos[i]
            j = i - 1

            # Shift elements greater than the current task to the right until the correct position for the current task is found
            while j >= 0 and key_function(self.__todos[j]) > key_function(current_task):
                self.__todos[j + 1] = self.__todos[j]
                j -= 1
                
            # Place the current task in its correct position
            self.__todos[j + 1] = current_task

        # Update the session with the sorted list of tasks
        self.__update_session()

    def __sort_tasks_by_length(self):
        """Sort tasks by length using the insertion sort algorithm."""
        self.__insertion_sort(key_function=len)

    def __sort_tasks_by_characters(self):
        """Sort tasks by characters using the insertion sort algorithm."""
        self.__insertion_sort(key_function=str)

    def get_todos(self):
        """Retrieve the current list of tasks."""
        return self.__todos

    def add_task(self, task):
        """Add a task to the ToDo list."""
        self.__add_task(task)

    def delete_task(self, index):
        """Delete a task from the ToDo list by index."""
        self.__delete_task(index)

    def sort_tasks_by_length(self):
        """Sort tasks by length."""
        self.__sort_tasks_by_length()

    def sort_tasks_by_characters(self):
        """Sort tasks by characters."""
        self.__sort_tasks_by_characters()


@app.route('/')
def home():
    """Redirects the user to the dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create an instance of the LoginForm
    form = LoginForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Query the database for a user with the provided username
        user = User.query.filter_by(username=form.username.data).first()

        # If a user is found, check the password
        if user:
            # Check if the hashed password matches the input password
            if bcrypt.check_password_hash(user.password, form.password.data):
                # Log in the user and redirect to the dashboard
                login_user(user)
                return redirect(url_for('dashboard'))

    # Render the login template with the form (initial or after unsuccessful login)
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Create an instance of the PromptForm
    form = PromptForm()

    # Process the prompt from the user
    DashboardRoute.process_form(form)
    return DashboardRoute.render_template(form)


@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    output = session.get('output', '')

    # If output is not present, redirect to the dashboard
    if not output:
        return redirect(url_for('dashboard'))

    form = request.form  # Assuming you are using request.form to access form data

    tutor = QuizTutor()
    quiz_content = tutor.generate_quiz(output)

    # Split the quiz content into lines and filter out empty lines
    quiz_lines = [line.strip() for line in quiz_content.split('\n') if line.strip()]

    # Create a 2D list to store questions, choices, and answers
    quiz_data = [quiz_lines[i:i+7] for i in range(0, len(quiz_lines), 7)]

    # Retrieve the first set of questions, choices, and answers
    current_quiz = quiz_data[0]

    # Extracting data from the current quiz set
    question = current_quiz[0]
    choices = current_quiz[1:-1]
    correct_answer = current_quiz[-1]

    user_answer = request.form.get('answer')

    # Check if the form has been submitted and compare user's answer with the correct answer
    if user_answer:
        is_correct = user_answer == correct_answer
    else:
        is_correct = None

    # Return the result as JSON if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result={'is_correct': is_correct, 'correct_answer': correct_answer})

    return render_template('quiz.html', output=output, question=question, choices=choices,
                           correct_answer=correct_answer)


@app.route('/todo', methods=['GET', 'POST'])
def todo():
    # Create an instance of ToDoHandler
    todo_handler = ToDoHandler()

    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        # Check which button was clicked in the form
        if 'add' in request.form:
            # Get the task from the form and add it to the ToDo list
            task = request.form.get('task')
            todo_handler.add_task(task)
        elif 'delete' in request.form:
            # Get the task index from the form and delete the task
            task_index = int(request.form.get('delete'))
            todo_handler.delete_task(task_index)
        elif 'sort_length' in request.form:
            # Sort tasks by length
            todo_handler.sort_tasks_by_length()
        elif 'sort_characters' in request.form:
            # Sort tasks by characters
            todo_handler.sort_tasks_by_characters()

    # Retrieve the current list of tasks
    todos = todo_handler.get_todos()

    # Render the 'todo.html' template with the tasks
    return render_template('todo.html', todos=todos)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # Clear the ToDo list before logging out
    session.pop('todos', None)
    
    # Log the user out of thier session
    logout_user()

    # Redirect the user back to the login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create an instance of the RegisterForm
    form = RegisterForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Generate a hashed password using bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data)

        # Create a new user with the provided username and hashed password
        new_user = User(username=form.username.data, password=hashed_password)

        # Add the new user to the database and commit changes
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful registration
        return redirect(url_for('login'))

    # Render the registration template with the form (initial or after unsuccessful registration)
    return render_template('register.html', form=form)


@app.route('/about', methods=['GET', 'POST'])
def about():
    # Render the about us page
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
