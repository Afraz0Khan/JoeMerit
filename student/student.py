import os
import ast
import MySQLdb
from textwrap import dedent

from student.helpers_student import *
from student.options_student import *
from student.sql_functions_student import *

db = MySQLdb.connect(host = "localhost", user = "root", passwd = os.environ['sqlpwd'])
cursor = db.cursor()

#table name template = "student_id | student_pw"

cursor.execute("SHOW DATABASES")
if ('students', ) not in cursor.fetchall():
    cursor.execute("CREATE DATABASE students")
    db.commit()

#login/sign_up process
while True:
    cursor.execute("USE students")
    display_options(first_prompt)

    first_choice = get_choice(first_prompt)

    if first_choice == 1:

        while True:
            login_id = input("Enter a username: ")

            cursor.execute("SHOW TABLES")
            for table_name in cursor.fetchall():
                if table_name.split(" | ")[0] == login_id:
                    print("This username has already been taken. Please choose a different username\n")
                    break
            else:
                break
                
        login_pw = confirm_password()

        # still have to add table columns. Might add datetime to store when their acc/ID was created.
        cursor.execute(f"CREATE TABLE {get_table_name(login_id, login_pw)} (test_name VARCHAR(20), subj_ans VARCHAR(1000), obj_ans DECIMAL(1),  subj_score DECIMAL(3), obj_score DECIMAL(3)")
        print("New ID created")
        logged_in = True

    else:
        login_id = input("Enter your student ID: ")
        login_pw = input("Enter your password: ")

        cursor.execute("SHOW TABLES")
        for table_name in cursor.fetchall():
            if get_table_name(login_id, login_pw) == table_name:
                print("Logged in successfully")
                logged_in = True
        else:
            print("The entered credentials may be wrong or you might not have an account.")
            logged_in = False
    
    if logged_in:
        break



#Logged in, starting test choosing, attempting and result viewing process
while True:

    display_options(second_prompt)
    
    prompt_choice = get_choice(second_prompt)
    
    if prompt_choice == 1:

        while True:

            # displaying available tests and getting a test choice for them to attempt
            test_dict = get_test_name_dict()

            display_options(test_dict)
            choice = get_choice(test_dict)

            cursor.execute("USE admin")
            cursor.execute(f"SELECT * from {test_dict[choice]}")
            questions = cursor.fetchall()

            obj = {"num": 0, "correct": 0}
            subj = {}

            #q_no: answer_chosen
            obj_ans = {}

            for question in questions: # may or may not use while True later to let the student move back and forth b/w questions
                """
                question
                0 = question number
                1 = type
                2 = question
                3 = weightage
                4 = word limit
                5 = options
                6 = answer
                """
            
                display = f"""
                {question[0]}) {question[2]} [{question[3]}]
                """

                if question[1] == "obj":
                    obj["num"] += 1
                    display += "\n\n"

                    for count, option in enumerate(question[5].split(" | "), start = 1):
                        display += f"{count}. {option}\n"

                else:
                    if question[4] is not None:
                        display += f"Word limit: {question[4]} words\n"
            
                print(dedent(display))

                while True:
                    answer = input("\nYour answer: ")

                    if question[1] == "obj":

                        if not answer.isdigit():
                            print("Please enter the option number to answer an objective type question")
                            continue
                    
                        if int(answer) not in range(1, 5):
                            print("Invalid option")
                            continue
                
                    else:
                        if " | " in answer:
                            print('Your answer cannot contain " | " in it.')
                            continue

                        if question[4] is not None:
                            if len(answer.split()) > question[4]:
                                print(f"Your answer is {len(answer)} words long, please keep it under the word limit of {question[4]} words")
                                continue
                    
                        subj[question[0]] = answer

                    break

                if question[1] == "obj":
                    obj_ans[question[0]] = answer

                    if int(answer) == int(question[6]):
                        obj["correct"] += 1
        
            display = "The test is now over"
            if obj["num"]:
                display += f". Your objective score was {obj['correct']}/{obj['num']}"
        
            print(display)

            cursor.execute("USE student")
            cursor.execute(f'INSERT INTO {get_table_name(login_id, login_pw)} VALUES ({test_dict[choice]}, {str(subj)}, {str(obj_ans)}, "NULL", {str(obj)})')

    elif prompt_choice == 2:

        while True:

            while True:

                if not logged_in:
                    print("Please log in again:")
                    login_id = input("Enter your student ID: ")
                    login_pw = input("Enter your password: ")

                    cursor.execute("SHOW TABLES")
                    for table_name in cursor.fetchall():
                        if get_table_name(login_id, login_pw) == table_name:
                            print("Logged in successfully")
                            logged_in = True  
                    else:
                        print("The entered credentials may be wrong or you might not have an account.")
                        logged_in = False
                
            
            if logged_in:
                cursor.execute('USE students')
                tests = get_test_name_dict()
                display_options(tests)

                test_name = get_choice(tests)

                cursor.execute(f'SELECT obj_score, subj_score FROM {get_table_name(login_id, login_pw)} WHERE test_name = {test_name}')

                score_data = cursor.fetchall()

                if (score_data[0] == 'NULL') and (score_data[1]) == 'NULL':
                    print('There is no data for you corresponding to this test. Please confirm if you have attempted this test successfully')
                    
                elif score_data[0] == 'NULL':
                    print(f'Your subjective score for this test is {score_data[1]}')
                    
                elif score_data[1] == 'NULL':
                    print(f'Your objective score for this test is {score_data[0]}')

                else:
                    print(f'Your objective score for this test: {score_data[0]}')
                    print(f'Your subjective score for this test: {score_data[1]}')

                break





            




