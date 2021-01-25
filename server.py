from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
import psycopg2
import time
import psycopg2
from psycopg2._psycopg import cursor

from data_manager import print_questions, vote_sql, sort_questions, edit_sql, add_image_sql, delete_question_sql, print_comments, \
    add_comment_sql, edit_comment_sql, delete_comment_sql, get_question_by_title, get_tags, print_comment_by_id, check_login, registration_form

import util
app = Flask(__name__, template_folder="html files", )
app.secret_key = 'secret key'

# @app.route("/")
# def main_page():
#     return render_template("main.html")
SORTIN_METHODS = {'id','title','submission_time','message','view_number','vote_number'}
DIRECTIONS = {'asc','desc'}




@app.route("/", methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db_password = check_login(email)['password']
        check_pw = bcrypt.checkpw(password.encode('utf8'), db_password.encode('utf8'))
        if check_pw:
            session['username'] = email
            return redirect(url_for('list_page'))
        else:
            return render_template('login_form.html', bad_login=True)

    elif request.method == 'GET':
        return render_template('login_form.html')


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf8'), salt)
        decoded = hashed.decode('utf8')
        username = request.form['username']
        registration_form(email, username, decoded)
        session['username'] = email
        return redirect(url_for('list_page'))
    elif request.method == 'GET':
        return render_template('registration.html')

@app.route('/logout', methods = ['POST'])
def logout():
    session.pop('username')
    return redirect(url_for('login'))

#sciezka odpowiadajaca za wyswietlnie listy pytań oraz umożliwia sortowanie.
@app.route("/list")
def list_page():
    if 'username' in session:
        user_name = session['username']
        COMMENTS = print_comments()
        QUESTION_TAGS = get_tags()
        user_arguments = dict(request.args) # pobranie argumentów
        user_conditions = [
            "order_by" in user_arguments,
            "order_direction" in user_arguments,
        ] # lista dla sprawdzenia czy w linku są te argumenty

        if all(user_conditions): # sprawdzamy czy są wszystkie argumenty i czy są takie jak trzeba
            order_by = user_arguments["order_by"]
            order_direction = user_arguments["order_direction"] # jak są dobre, to pobieramy
            data_conditons = [
                order_by in SORTIN_METHODS,
                order_direction in DIRECTIONS,
            ] # list dla sprawdzenia wartości argumentów
            if all(data_conditons): # sprawdzanie czy całe data conditions to True
                QUESTIONS = sort_questions(order_by, order_direction)
                return render_template('list.html', questions=QUESTIONS, comments=COMMENTS, tags=QUESTION_TAGS,
                                       username=user_name )
        else:
            search_questions = request.args.get('search-for-question')
            if search_questions:
                details = get_question_by_title(search_questions)
            else:
                details = print_questions()
            return render_template('list.html', questions=details, comments=COMMENTS, tags=QUESTION_TAGS,
                                   username=user_name)
    else:
        return redirect(url_for('login'))



@app.route('/question/<question_id>/vote_up',methods=['POST']) # problem
def vote_up(question_id):
    vote_sql(question_id)

    return redirect(url_for('list_page'))

@app.route('/question/<question_id>/vote_down',methods=['POST'])
def vote_down(question_id):
    vote_sql(question_id, add=False)

    return redirect(url_for('list_page'))

@app.route('/question/<question_id>/delete', methods=['POST'])
def delete_question(question_id):
    delete_question_sql(question_id)

    return redirect(url_for('list_page'))

@app.route('/question/<question_id>/edit', methods = ['POST', 'GET'])
def edit_question(question_id):

    if request.method == 'GET':
        questions = print_questions()[int(question_id)]
        return render_template('edit.html', question=questions)
    elif request.method == 'POST':
        to_dict = request.form.to_dict()
        edit_sql(question_id, **to_dict)
        return redirect(url_for('list_page'))
    else:
        return "Method not recognized"

@app.route('/question/<question_id>/image', methods = ['POST', 'GET'])
def add_image(question_id):
    if request.method == 'GET':
        questions = print_questions()[int(question_id)]
        return render_template('image.html', question=questions)
    elif request.method == 'POST':
        new_image = request.form['image']
        add_image_sql(new_image, question_id)
        return redirect(url_for('list_page'))
    else:
        return "Method not recognized"

@app.route('/question/<question_id>/new_comment', methods = ['GET', 'POST'])
def add_comment(question_id):
    if request.method == 'GET':
        return render_template('comment.html', question_id=question_id)
    elif request.method == 'POST':
        response = request.form.to_dict()
        add_comment_sql(question_id, response['message'])
        return redirect(url_for('list_page'))
    else:
        return "Method not recognized"


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if request.method == 'GET':
        comments = print_comment_by_id(comment_id)
        print(comments)
        return render_template('edit_comment.html', comment=comments)
    elif request.method == 'POST':
        to_dict = request.form.to_dict()
        edit_comment_sql(comment_id, **to_dict)
        return redirect((url_for('list_page')))

@app.route('/comment/<comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    delete_comment_sql(comment_id)

    return redirect((url_for('list_page')))



@app.route('/question_status/<question_id>_<view_add>')
def see_question(question_id, view_add):
    if request.method == 'GET':
        questions = print_questions()[int(question_id)]
        return render_template('question_status.html', question=questions)
    elif request.method == 'POST':
        to_dict = request.form.to_dict()
        edit_sql(question_id, **to_dict)
        return redirect(url_for('list_page'))
    else:
        return "Method not recognized"


# @app.route('/question_status/<question_id>/new_answer', methods=["GET", "POST"])
# def add_answer(question_id):
#     if request.method == "GET":
#         questions = print_questions()[int(question_id)]
#         return render_template("add_answer.html", question=questions)
#     elif request.method == "POST":
#         answer = util.get_default_answer()
#         title = request.form.get('title')
#         message = request.form.get("message")
#         image = request.form.get("image")
#         add_questions(title, message, image)
#         return redirect(url_for('list_page'))
#












if __name__ == "__main__":
    app.run(debug=True)
