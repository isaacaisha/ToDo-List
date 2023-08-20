from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "any-string-you-want-just-keep-it-secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'  # SQLite database

db = SQLAlchemy(app)

# ------------------------------------------------------ VARIABLES ----------------------------------------------------#
time_sec = time.localtime()
current_year = time_sec.tm_year
# getting the current date and time
current_datetime = datetime.now()
# getting the time from the current date and time in the given format
current_time = current_datetime.strftime("%a %d %B")


# -------------------------------------------------------- CLASS ------------------------------------------------------#
class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, text):
        self.text = text


class CreateTodo(FlaskForm):
    create_todo = StringField('Create your To-Do list below:')
    submit = SubmitField()


class DeleteTodo(FlaskForm):
    submit = SubmitField()


with app.app_context():
    db.create_all()


# ------------------------------------------------------ FUNCTIONS ----------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def todo_create():
    create_todo_form = CreateTodo()
    btn_delete_form = DeleteTodo()

    if create_todo_form.validate_on_submit():
        todo_text = create_todo_form.create_todo.data
        new_todo = TodoItem(text=todo_text)
        db.session.add(new_todo)
        db.session.commit()

    todos = TodoItem.query.filter_by(completed=False).all()
    completed_todos = TodoItem.query.filter_by(completed=True).all()

    return render_template('index.html', year=current_year, date=current_time,
                           create_todo_form=create_todo_form, todos=todos,
                           completed_todos=completed_todos, btn_delete_form=btn_delete_form)


@app.route('/clear_done', methods=['POST'])
def clear_done():
    try:
        # Get the list of task IDs to delete from the request JSON data
        data = request.get_json()
        todo_ids = data.get('todoIds', [])

        # Delete completed todos from the database
        for todo_id in todo_ids:
            completed_todo = db.session.query(TodoItem).get(todo_id)

            if completed_todo:
                db.session.delete(completed_todo)

        db.session.commit()  # Commit changes after all deletions

        # Return a success message in JSON format
        return jsonify({'message': 'To-Do items cleared successfully'})

    except Exception as e:
        # Handle any exceptions and log the error
        print(f"Error in clear_done route: {str(e)}")
        # Return a 500 Internal Server Error
        return jsonify({'error': 'An error occurred while clearing To-Do items'}), 500


@app.route('/clear_all', methods=['POST'])
def clear_all():
    try:
        # Delete all todos from the database
        db.session.query(TodoItem).delete()
        db.session.commit()

        # Redirect the user back to the same page
        return redirect(url_for('todo_create'))

    except Exception as e:
        # Handle any exceptions and log the error
        print(f"Error in clear_all route: {str(e)}")
        return jsonify({'error': 'An error occurred while clearing all To-Do items'}), 500  # Return a 500 Internal Server Error


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
