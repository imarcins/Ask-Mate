import data_manager
import csv
from datetime import datetime


def add_new_id(table):
    questions = data_manager.read_csv(table)
    id_f = int(len(questions)) + 1
    return id_f


Qheaders = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]  # QUESTIONS[0]
Aheaders = ["id", "submission_time", "vote_number", "question_id", "message", "image"]


def get_submission_time():
    return datetime.today().strftime('%Y-%m-%d-%H:%M:%S')


def get_default_question():
    return {"id": None, "submission_time": "00-00-00", "view_number": 0, "vote_number": 0, "title": "title",
            "message": "message"}


def get_default_answer():
    return {"id": None, "submission_time": "00-00-00", "vote_number": 0, "question_id": 0, "message": "message",
            "image": None}


def sorting(questions, value, order):
    return sorted(questions, key=lambda question: question[value].lower(), reverse=order)


def add_view(view):
    return int(view) + 1
