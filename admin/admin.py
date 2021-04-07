import os
from datetime import datetime

import MySQLdb

from admin.options_admin import *
from admin.helpers_admin import *
from admin.sql_functions_admin import *

db = MySQLdb.connect(host = "localhost", user = "root", passwd = os.environ['sqlpwd'])
cursor = db.cursor()

cursor.execute("SHOW DATABASES")
if ('admin', ) not in cursor.fetchall():
    cursor.execute("CREATE DATABASE admin")
    db.commit()

cursor.execute("USE admin")

cursor.execute("SHOW TABLES")
if ('master', ) not in cursor.fetchall():
    cursor.execute("CREATE TABLE master (test_name VARCHAR(20), subj_ques DECIMAL(2,0), obj_ques DECIMAL(2,0), num_ques DECIMAL(2,0), max_marks DECIMAL(3,1), created_at TIMESTAMP)")
    db.commit()


print("\nWelcome to the admin panel for JoeMerit\nPlease choose an option:\n")
while True:
    display_options(main_options)
    choice = get_choice(main_options)

    if choice == 1:
        test_name = input("Enter the name of the test: ")
        test_name.replace(" ", "_")

        cursor.execute("USE admin")
        cursor.execute("SHOW TABLES")

        if (test_name, ) in cursor.fetchall():
            print(f"A test named {test_name} already exists")
            continue
        
        cursor.execute(f"CREATE TABLE {test_name} (q_no DECIMAL(2), type VARCHAR(4), question VARCHAR(120), weightage DECIMAL(1), word_limit DECIMAL(3), options VARCHAR(300), answer DECIMAL(1))")

        data = interpret_output(add_questions(test_name))

        cursor.execute(f"INSERT INTO master VALUES ({test_name}, {data['subj_ques_num']}, {data['obj_ques_num']}, {data['subj_ques_num'] + data['obj_ques_num']}, {datetime.now().timestamp()})")
        db.commit()

    elif choice == 2:

        while True:
            display_options(view_options)
            subchoice = get_choice(view_options)

            if subchoice == 1:
                view_tests()

            elif subchoice == 2:
                test_name = input("Enter the test name you want to see the questions of: ")
                view_questions(test_name)

            elif subchoice == 3:
                test_name = input("Enter the test name you want to add a question to: ")
                add_questions(test_name)

            elif subchoice == 4:
                test_name = input("Enter the test name you want to remove a question from")
                view_questions(test_name)
                question_number = int(input("Enter the question number you want to remove: "))
                remove_question(test_name, question_number)

            elif subchoice == 5:
                testName = input('Enter name of test whose properties are to be modified: ')
                ques_no = input('Enter question number to be edited: ')
                modify_question(testName, ques_no)

            elif subchoice == 6:
                break

    elif choice == 3:
            
        test_name = input("Enter the test name which you want to delete: ")

        cursor.execute("SHOW TABLES")
        if (test_name, ) not in cursor.fetchall():
            print(f"A test called {test_name} does not exist")
            
        else:
            delete_test(test_name)


    elif choice == 4:
        while True:

            while True:

                test_name = input("Enter the exact test name for which you want to grade the class: ")
                cursor.execute("USE admin")
                cursor.execute("SHOW TABLES")


                if (test_name ,) not in cursor.fetchall():
                    print("This test does not exist or is invalid. Please enter the correct test name.")
                    break
                
                cursor.execute("USE students")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()

                for student in tables:
            
                    student_name = student[0].split(" | ")[0]
                    print(f"Grading test for {student_name}.")


                    
                    cursor.execute(f"SELECT * FROM {student} WHERE test_name = {str(test_name)}")
                    horizontal = cursor.fetchone()
                    all_answers = horizontal[1]

            
                    #question extraction

                    cursor.execute("USE admin")

                    cursor.execute(f"SELECT question FROM {test_name} WHERE type = 'subj'")
                    all_questions = cursor.fetchall()
                    cursor.execute(f"SELECT weightage FROM {test_name} WHERE type = 'subj'")
                    all_weightages = cursor.fetchall()

                    score_dict = {}

                    #single question-answer extraction and display
                    for i in range(0,(len(all_questions)[0]+1)):

                        print(f"Question:\n{all_questions[i]}")

                        print(f"Given answer:\n{all_answers[i]}")

                        print(f"weightage: {all_weightages[i]}")

                        while True:

                            score = input("Enter score: ")

                            if score.isalpha():
                                print("The score should be an integer. Try again.")
                                continue
                    
                            if int(score) > int(all_weightages[i]):
                                print("The score cannot be more than the weightage. Try again.")
                                continue

                            score_dict[i] = score

                            break


                    cursor.execute("USE students")
                    #make a dict to store the respective scores

                    cursor.execute(f"UPDATE {student} SET sub_score = {str(score_dict)} WHERE test_name = {test_name}")
                
                print("You have marked all answers.")
                break
            break





    elif choice == 5:

        
        while True:

            test_name = input("Enter test name for which results are to be viewed: ")
            
            #checking if the test exists
            cursor.execute("USE admin")
            cursor.execute("SHOW TABLES")
            if (test_name, ) not in cursor.fetchall():
                print("The entered test name does not exist. Please enter a valid test.")
                break

                    

            cursor.execute("USE students")       
            cursor.execute("SHOW TABLES")

            all_tables = cursor.fetchall()            

            for user in all_tables:

            #getting total score for one student and displaying it
                #initializing da ting

                cursor.execute(f"SELECT subj_score FROM {(user ,)[0]} WHERE test_name = {test_name}")
                scores = dict(cursor.fetchall()[0])

                total_score = get_total_score(scores)
                
                student_username = user[0].split(" | ")[0]

                #displaying da ting
                print(f"Subjective score for {student_username} : {total_score}\n")
                
            cont = input("Do you want to conitnue for other tests? (y/n)")

            if cont.lower() == "y":
                continue

            elif cont.lower() == "n":
                break







