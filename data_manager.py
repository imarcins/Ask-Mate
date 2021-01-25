import os
import psycopg2
from typing import List, Dict
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import datetime
# PATH = sys.path[0]
# # def to_dict(reader):
# #     for line in reader:
# #         ID,submission_time,view_number,vote_number,title,message,image = line
# #         yield {
# #             'id': ID,
# #             "submission_time": submission_time,
# #             "view_number": view_number,
# #             "vote_number": vote_number,
# #             "title": title,
# #             "message": message,
# #             "image": image,
# #         }
#
# # def read_csv(file_name):
# #     file_path = rf"{PATH}\DB\{file_name}"
# #     with open(file_path,'r') as csv_file:
# #         data_from_csv = csv.reader(csv_file)
# #         dictionary = list(to_dict(data_from_csv))[1:]
# #         return dictionary
#
# def to_dict(reader):
#     to_return = dict()
#     for line in reader:
#         ID,submission_time,view_number,vote_number,title,message,image = line
#         to_return[ID] = {
#             'id': ID,
#             "submission_time": submission_time,
#             "view_number": int(view_number),
#             "vote_number": int(vote_number),
#             "title": title,
#             "message": message,
#             "image": image,
#         }
#     return to_return
#
# def read_csv(file_name):
#     file_path = rf"{PATH}\DB\{file_name}"
#     with open(file_path,'r') as csv_file:
#         data_from_csv = list(csv.reader(csv_file))[1:]
#         dictionary = to_dict(data_from_csv)
#         return dictionary
#
#
# def write_csv(file_name,data_to_save):
#     file_path = rf"{PATH}\DB\{file_name}"
#     with open(file_path,'w') as csv_file:
#         csv_file.write('id,submission_time,view_number,vote_number,title,message,image\n')
#         for line in data_to_save.values():
#             ID = line['id']
#             submission_time = line['submission_time']
#             view_number = str(line['view_number'])
#             vote_number = str(line['vote_number'])
#             title = f"\"{line['title']}\""
#             message = f"\"{line['message']}\""
#             image = f"\"{line['image']}\""
#             csv_file.write(','.join([ID,submission_time,view_number,vote_number,title,message,image]) + '\n')
#
#
# def sort_dict(dictionary,key,rev):
#     to_sort = dictionary.values()
#     if rev == 'asce':
#         sort = sorted(to_sort,key=lambda column: column[key])
#     else:
#         sort = sorted(to_sort,key=lambda column: column[key],reverse=True)
#     return sort
#
# def add_new_id(table):
#     row_count = len(table)
#     row_count_f = row_count / 2 +1
#     return str(int(row_count_f))
#
#
# def find_line(table, question_id, id_number):
#     line = 0
#     if line < len(table) - 1 and table[line][id_number] != str(question_id):
#         line += 1
#     return table[line]

def get_connection():
    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')

    any_variables_defined = user_name and password and host and database_name

    if any_variables_defined:
        return f'postgresql://{user_name}:{password}@{host}/{database_name}'
    else:
        raise KeyError('Missing variables')

def open_database():
    try:
        connection_string = get_connection()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print("Database connection issue")
        raise exception
    return connection

def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value
    return wrapper

@connection_handler
def print_questions(cursor: RealDictCursor):
    query = "SELECT * FROM question ORDER by id"
    cursor.execute(query)
    return cursor.fetchall()


@connection_handler
def sort_questions(cursor: RealDictCursor, order_by, order_direction):
    query = f"SELECT * FROM question ORDER BY {order_by} {order_direction} "
    cursor.execute(query)
    return cursor.fetchall()


@connection_handler
def vote_sql(cursor:RealDictCursor, question_id, add=True):
    query = f"SELECT vote_number FROM question WHERE id={question_id}"
    cursor.execute(query)
    response = dict(cursor.fetchall()[0])
    if add:
        vote_number = response['vote_number'] + 1
    else:
        vote_number = response['vote_number'] - 1
    query = f"UPDATE question SET vote_number = {vote_number} WHERE id={question_id}"
    cursor.execute(query)

@connection_handler
def edit_sql(cursor: RealDictCursor, question_id, title, message, image):
    query = f"UPDATE question SET title = '{title}', message = '{message}', image = '{image}' WHERE id = {question_id}"
    cursor.execute(query)

@connection_handler
def add_image_sql(cursor: RealDictCursor, image, question_id):
    query = f"UPDATE question SET image = '{image}' WHERE id = {question_id}"
    cursor.execute(query)

@connection_handler
def delete_question_sql(cursor: RealDictCursor, question_id):
    query = f"DELETE FROM question WHERE id = {question_id}"
    cursor.execute(query)

@connection_handler
def print_comments(cursor: RealDictCursor):
    query = "SELECT * FROM comment"
    cursor.execute(query)
    return cursor.fetchall()

@connection_handler
def add_comment_sql(cursor: RealDictCursor, question_id, message, email):
    submission_time = datetime.datetime.now()
    query = f"INSERT into comment (question_id, message, submission_time) VALUES ({question_id}, '{message}', " \
            f"'{submission_time}' )"
    cursor.execute(query)

@connection_handler
def edit_comment_sql(cursor: RealDictCursor, comment_id, message):
    query = f"UPDATE COMMENT SET message = '{message}' WHERE id = {comment_id}"
    cursor.execute(query)

@connection_handler
def delete_comment_sql(cursor: RealDictCursor, comment_id):
    query = f"DELETE FROM comment WHERE id = {comment_id}"
    cursor.execute(query)

@connection_handler
def get_question_by_title(cursor: RealDictCursor, search):
    query = f"SELECT * FROM question WHERE title LIKE '{search}'"
    cursor.execute(query)
    return cursor.fetchall()

@connection_handler
def get_tags(cursor: RealDictCursor):
    query = "SELECT question_id, name FROM question_tag INNER JOIN tag ON question_tag.tag_id = tag.id"
    cursor.execute(query)
    return cursor.fetchall()


@connection_handler
def print_comment_by_id(cursor: RealDictCursor, comment_id):
    query = f"SELECT * FROM comment WHERE id = {comment_id}"
    cursor.execute(query)
    return cursor.fetchone()

@connection_handler
def check_login(cursor: RealDictCursor, email):
    query = f"SELECT password FROM users WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchone()
@connection_handler
def check_users(cursor: RealDictCursor, email):
    query = f"SELECT ID from users WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchone()


@connection_handler
def registration_form(cursor: RealDictCursor, email, username, password):
    query = f"INSERT into users (email, username, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, username, password))



@connection_handler
def check_user(cursor: RealDictCursor, email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchone()

@connection_handler
def user_list(cursor: RealDictCursor):
    query = "SELECT * FROM users"
    cursor.execute(query)
    return cursor.fetchall()

