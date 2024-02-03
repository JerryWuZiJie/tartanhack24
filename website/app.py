# Bangjie Xue
import sqlite3
from flask import Flask, render_template, request
import urllib.parse
import os
import pandas as pd
from pprint import pprint
import numpy as np
from sklearn.manifold import TSNE
from scipy.stats import spearmanr

def scoring(rank, df):
    
    def tsne_score(df):
        TSNEout = TSNE(n_components=2, method='exact').fit_transform(df)
        score = TSNEout[:, 0] - TSNEout[:, 1]

        return score
    
    df = (df - df.min(0))/(df.max(0) - df.min(0))
    
    #  spearsman corr
    corr = spearmanr(rank, df)[0][0][1:]
    df *= corr
    
    score = tsne_score(df)
    
    
    return corr, score

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

# Function for connecting to database
# def get_db_connection():
#     conn = sqlite3.connect('./database/data.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# Landing Page, show a list of features
@app.route('/', methods=['GET', 'POST'])
def index():
    param_names = ['Parking Friendliness', 'Biking Friendliness', 'Ease of Commute', 'Affordability', 'Safety']
    rank = ["Irrelevant", "Low", "Medium", "High"]
    global parameters
    if request.method == "POST":
        parameters = [request.form.get(param_name) for param_name in param_names]
        mapped_param = {
            '0':0,
            '1':0.25,
            '2':0.6,
            '3':1
            }
        
        df = pd.read_csv("/Users/JimXue/Desktop/tartanhack24/Datasets/post_processed.csv")
        # Normalize the data sum to 1
        for col in df.iloc[:, 3:]:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col] / df[col].sum()
            if df[col].dtype == object and df[col].str.contains('%').any():
                # Remove the percentage sign and convert to float
                df[col] = df[col].str.replace('%', '').astype(float) / 100
                # Now normalize
                df[col] = df[col] / df[col].sum()
            if df[col].dtype == object and df[col].str.contains('$').any():
                # Remove the percentage sign and convert to float
                df[col] = df[col].str.replace('[\$,]', '', regex=True).astype(float) / 100
                # Now normalize
                df[col] = df[col] / df[col].sum()
        # Data Selection
        drop_lst = ['SNAP_All_csv_Median_Home_Value_','Med__Val____00_in__10_Dollars_','SNAP_All_csv_Part_1_Crime_per_1',
                'SNAP_All_csv__Murder__2010_',
               'SNAP_All_csv__Rape__2010_', 'SNAP_All_csv__Robbery__2010_',
               'F_Agr__Assault__2010_', 'SNAP_All_csv__Burglary__2010_',
               'SNAP_All_csv__Auto_Theft__2010_', 'SNAP_All_csv__Drug_Violations__', 'SNAP_All_csv___Good___Excellent', 'SNAP_All_csv___Average_Conditio',
               'SNAP_All_csv___Poor___Derelict_', 'SNAP_All_csv_Landslide_Prone___', 'SNAP_All_csv_Woodland____of_lan', 'SNAP_All_csv_Cemetery____of_lan','Population (2010)', 'Miles of Major Roads',
               'Total Street Miles','Commute to Work: Drive Alone (2010)',
               'Commute to Work: Carpool/Vanpool (2010)',
               'Commute to Work: Public Transportation (2010)',
               'Commute to Work: Taxi (2010)', 'Commute to Work: Motorcycle (2010)',
               'Commute to Work: Bicycle (2010)', 'Commute to Work: Walk (2010)',
               'Commute to Work: Other (2010)', 'Work at Home (2010)','Neighborhood_2010_SQMILES','SNAP_All_csv_2009_Median_Income','Total Working Pop. (Age 16+) (2010)', 'SNAP_All_csv_Residential',]
        trash_lst = df[drop_lst]
        df.drop(columns=drop_lst, inplace=True)
        df.drop(columns=['Latitude', 'Longitude'], inplace=True)
        # Parking friendliness
        # (df.iloc[:, 12] + df.iloc[:, 13] - df.iloc[:, 14])/3
        # Bike friendliness
        # df.iloc[:, 2]
        # Ease of Commute
        # (df.iloc[:, 15] + df.iloc[:, 16])/2
        # Affordability
        # (-df.iloc[:, 5] + -df.iloc[:, 6] + df.iloc[:, 7] - df.iloc[:, 8])/4
        # Safety
        # (-df.iloc[:, 1] -df.iloc[:, 3] -df.iloc[:, 4] - df.iloc[:, 9] - df.iloc[:, 10] - df.iloc[:, 11])/6

        df["sum"] = mapped_param[parameters[0]]*(df.iloc[:, 12] + df.iloc[:, 13])/2 +\
            mapped_param[parameters[1]]*df.iloc[:, 2] +\
                mapped_param[parameters[2]]*(df.iloc[:, 15] + df.iloc[:, 16])/2 +\
                    mapped_param[parameters[3]]*(-df.iloc[:, 5] + -df.iloc[:, 6] + df.iloc[:, 7] - df.iloc[:, 8])/4 +\
                        mapped_param[parameters[4]]*(-df.iloc[:, 1] -df.iloc[:, 3] -df.iloc[:, 4] - df.iloc[:, 9] - df.iloc[:, 10] - df.iloc[:, 11])/6

        print(df.iloc[:,[0,-1]].values)
        df.sort_values('sum', ascending=False, inplace = True)
        # print(df.iloc[:,0].values)
        ranked_list = df.iloc[:,0].values
        
        # ranked_list = ['one', 'two', 'three', 'four', 'five'] 
        
        return render_template('index.html', parameters = parameters, ranked_list = ranked_list, param_names = param_names, rank = rank)
    else:
        parameters = ['0', '0', '0', '0', '0']
        ranked_list = ['Please adjust the parameters and submit!'] 
        return render_template('index.html', parameters = parameters, ranked_list = ranked_list, param_names = param_names, rank = rank)

@app.route('/details/<county>')
def details(county):
    # Get all the information of this course from each table
    detail1 = ['detail1', 'detail4']
    detail2 = ['detail2']
    detail3 = ['detail3']
    return render_template('details.html', county=county, detail1=detail1, detail2=detail2, detail3=detail3)



# # Concepts Page, display all concepts with course number in the database
# @app.route('/concepts/', methods=['GET', 'POST'])
# def concepts():
#     if request.method == "POST":
#         # If method is post, the user used filter function
#         # Encode result is used to accomadate spaces in some concept names
#         encoded_result = request.form.get("filter")
#         # Deconde the encoded result to the plain text format
#         result = urllib.parse.unquote(encoded_result)
#         conn = get_db_connection()
#         # Retrive the courses that contains the concept submitted by the user
#         cctable = conn.execute("SELECT * FROM courses_concepts WHERE course_id IN (SELECT course_id FROM courses_concepts WHERE concept LIKE ?) ORDER BY course_id ASC", (result,)).fetchall()
#         conn.close()
#         return render_template('concepts.html', cctable=cctable)
#     else:
#         # If first entered this page, display all concepts
#         conn = get_db_connection()
#         # Retrive all concepts from the courses_concepts table in database, order by asceding order
#         cctable = conn.execute('SELECT * FROM courses_concepts ORDER BY course_id ASC').fetchall()
#         conn.close()
#         return render_template('concepts.html', cctable=cctable)

# # Skills Page, similar to the concepts page
# @app.route('/skills/', methods=['GET', 'POST'])
# def skills():
#     if request.method == "POST":
#         encoded_result = request.form.get("filter")
#         result = urllib.parse.unquote(encoded_result)
#         conn = get_db_connection()
#         cctable = conn.execute("SELECT * FROM courses_skills WHERE course_id IN (SELECT course_id FROM courses_skills WHERE skill LIKE ?) ORDER BY course_id ASC", (result,)).fetchall()
#         conn.close()
#         return render_template('skills.html', cctable=cctable)
#     else:
#         conn = get_db_connection()
#         cctable = conn.execute('SELECT * FROM courses_skills ORDER BY course_id ASC').fetchall()
#         conn.close()
#         return render_template('skills.html', cctable=cctable)

# # Maker Activities Page, similar to the concepts page
# @app.route('/makers/', methods=['GET', 'POST'])
# def makers():
#     if request.method == "POST":
#         encoded_result = request.form.get("filter")
#         result = urllib.parse.unquote(encoded_result)
#         conn = get_db_connection()
#         cctable = conn.execute("SELECT * FROM courses_makers WHERE course_id IN (SELECT course_id FROM courses_makers WHERE maker LIKE ?) ORDER BY course_id ASC", (result,)).fetchall()
#         conn.close()
#         return render_template('makers.html', cctable=cctable)
#     else:
#         conn = get_db_connection()
#         cctable = conn.execute('SELECT * FROM courses_makers ORDER BY course_id ASC').fetchall()
#         conn.close()
#         return render_template('makers.html', cctable=cctable)

# # Ethics Activities Page, similar to the concepts page
# @app.route('/ethics/', methods=['GET', 'POST'])
# def ethics():
#     if request.method == "POST":
#         encoded_result = request.form.get("filter")
#         result = urllib.parse.unquote(encoded_result)
#         conn = get_db_connection()
#         cctable = conn.execute("SELECT * FROM courses_ethics WHERE course_id IN (SELECT course_id FROM courses_ethics WHERE ethic LIKE ?) ORDER BY course_id ASC", (result,)).fetchall()
#         conn.close()
#         return render_template('ethics.html', cctable=cctable)
#     else:
#         conn = get_db_connection()
#         cctable = conn.execute('SELECT * FROM courses_ethics ORDER BY course_id ASC').fetchall()
#         conn.close()
#         return render_template('ethics.html', cctable=cctable)

# # Entreprenualship Page, similar to the concepts page
# @app.route('/entreps/', methods=['GET', 'POST'])
# def entreps():
#     if request.method == "POST":
#         encoded_result = request.form.get("filter")
#         result = urllib.parse.unquote(encoded_result)
#         conn = get_db_connection()
#         cctable = conn.execute("SELECT * FROM courses_entreps WHERE course_id IN (SELECT course_id FROM courses_entreps WHERE entrep LIKE ?) ORDER BY course_id ASC", (result,)).fetchall()
#         conn.close()
#         return render_template('entreps.html', cctable=cctable)
#     else:
#         conn = get_db_connection()
#         cctable = conn.execute('SELECT * FROM courses_entreps ORDER BY course_id ASC').fetchall()
#         conn.close()
#         return render_template('entreps.html', cctable=cctable)

# # Courses Page, display all courses in the database
# @app.route('/courses/')
# def courses():
#     conn = get_db_connection()
#     cctable = conn.execute('SELECT * FROM courses').fetchall()
#     conn.close()
#     return render_template('courses.html', cctable=cctable)

# # Instructors Page, display all instructors information in the database
# @app.route('/instructors/')
# def instructors():
#     conn = get_db_connection()
#     cctable = conn.execute('SELECT * FROM instructors').fetchall()
#     conn.close()
#     return render_template('instructors.html', cctable=cctable)

# # Prereq view, user submit a course number, and the prereq tree up to 8 levels is displayed.
# @app.route('/prereqs/', methods=["GET", "POST"])
# def prereqs():
#     # If entered by POST, a course number has been selected, generate prereq tree.
#     if request.method == "POST":
#         # result now has the course number submitted by user
#         result = request.form.get("number")
#         conn = get_db_connection()
#         # select the name of the course number submitted, for validation purpose only
#         result_name = conn.execute("SELECT name FROM courses WHERE number = ?", (result,)).fetchall()
#         # Retrieve the prereq courses for the result course number
#         result_prereq = conn.execute("SELECT coreq, prereq_text FROM prereqs WHERE course_id = ? LIMIT 1", (result,)).fetchall()
#         # Retrieve the semester info of the course
#         result_semester = conn.execute("SELECT semester_id FROM courses_instructors WHERE course_id = ? LIMIT 1", (result,)).fetchall()
#         # Retrieving the full prereq list - prereq_text and coreq info used in html for displaying the Coreq and Prereq text in the pop up.
#         full_list = conn.execute('SELECT * FROM prereqs').fetchall()
#         # Retriving the course numbers level by level, finding the prereqs of the prereqs, up to 8 levels
#         prereq1 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id = ?", (result,)).fetchall()
#         prereq2 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?)", (result,)).fetchall()
#         prereq3 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?))", (result,)).fetchall()
#         prereq4 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?)))", (result,)).fetchall()
#         prereq5 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?))))", (result,)).fetchall()
#         prereq6 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?)))))", (result,)).fetchall()
#         prereq7 = conn.execute("SELECT course_id, prereq_id, coreq, prereq_text, name FROM prereqs JOIN courses ON prereqs.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id IN (SELECT prereq_id FROM prereqs WHERE course_id = ?))))))", (result,)).fetchall()
#         conn.close()
#         # If using the entered course number can't retrive any data from database, invalid entry
#         if len(result_name) < 1:
#             # Redirect to apology page
#             return render_template('apology.html')
#         # Passing all the information retrived to the prereqed page
#         return render_template('prereqed.html', full_list=full_list, result_prereq=result_prereq, prereq1=prereq1, prereq2=prereq2, prereq3=prereq3, prereq4=prereq4, prereq5=prereq5, prereq6=prereq6, prereq7=prereq7, result=result, result_name=result_name, result_semester=result_semester)
#     else:
#         # If the user entered by GET, display the input prompt for entering course number.
#         return render_template("prereqs.html")

# # Cluster view, similar to prereq view, the displayed info is slightly different but the underlying structure is exactly the same.
# # Instead of retriving from the prereqs table, we are retriving from the clusters table.
# @app.route('/clusters/', methods=["GET", "POST"])
# def clusters():
#     if request.method == "POST":
#         result = request.form.get("number")
#         conn = get_db_connection()
#         result_name = conn.execute("SELECT name FROM courses WHERE number = ?", (result,)).fetchall()
#         result_prereq = conn.execute("SELECT coreq, prereq_text FROM prereqs WHERE course_id = ? LIMIT 1", (result,)).fetchall()
#         result_semester = conn.execute("SELECT semester_id FROM courses_instructors WHERE course_id = ? LIMIT 1", (result,)).fetchall()
        
#         full_list = conn.execute('SELECT * FROM prereqs').fetchall()

#         prereq1 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id = ?", (result,)).fetchall()
#         prereq2 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?)", (result,)).fetchall()
#         prereq3 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?))", (result,)).fetchall()
#         prereq4 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?)))", (result,)).fetchall()
#         prereq5 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?))))", (result,)).fetchall()
#         prereq6 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?)))))", (result,)).fetchall()
#         prereq7 = conn.execute("SELECT course_id, coreq, prereq_text, prereq_id, name FROM clusters JOIN courses ON clusters.prereq_id = courses.number WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id IN (SELECT prereq_id FROM clusters WHERE course_id = ?))))))", (result,)).fetchall()

#         conn.close()
#         if len(result_name) < 1:
#             return render_template('apology.html')
#         return render_template('clustered.html', full_list=full_list, result_prereq=result_prereq, prereq1=prereq1, prereq2=prereq2, prereq3=prereq3, prereq4=prereq4, prereq5=prereq5, prereq6=prereq6, prereq7=prereq7, result=result, result_name=result_name, result_semester=result_semester)
#     else:
#         return render_template("clusters.html")
    
# # Instructor View page, the user can enter an andrew id to generate all courses he/she teaches
# @app.route('/instructorview/', methods=["GET", "POST"])
# def instructorview():
#     if request.method == "POST":
#         andrew = request.form.get("andrew")
#         conn = get_db_connection()
#         # Retrive the information of this andrew id, for validation purpose below
#         test = conn.execute('SELECT * FROM instructors WHERE id = ?', (andrew,)).fetchall()
#         # Retrive all courses by this andrew id
#         courses = conn.execute("SELECT course_id FROM courses_instructors WHERE instructor_id = ?", (andrew,)).fetchall()
#         conn.close()
#         # Check if the andrew id exist in database
#         if len(test) < 1:
#             return render_template('apology.html')
#         return render_template('instructorviewed.html', andrew=andrew, courses=courses)
#     else:
#         # Render the input prompt page
#         return render_template("instructorview.html")

# # Bucket view page, display up to 5 columns of information in table format
# @app.route('/buckets/')
# def buckets():
#     conn = get_db_connection()
#     # Entire buckets table
#     cctable = conn.execute('SELECT * FROM buckets').fetchall()
#     # Select the course names and join them to the course numbers of each column to be concatenated for display in html.
#     c1 = conn.execute('SELECT column1, name AS name1 FROM buckets JOIN courses ON buckets.column1 = courses.number').fetchall()
#     c2 = conn.execute('SELECT column2, name AS name2 FROM buckets JOIN courses ON buckets.column2 = courses.number').fetchall()
#     c3 = conn.execute('SELECT column3, name AS name3 FROM buckets JOIN courses ON buckets.column3 = courses.number').fetchall()
#     c4 = conn.execute('SELECT column4, name AS name4 FROM buckets JOIN courses ON buckets.column4 = courses.number').fetchall()
#     c5 = conn.execute('SELECT column5, name AS name5 FROM buckets JOIN courses ON buckets.column5 = courses.number').fetchall()
#     conn.close()
#     return render_template('buckets.html', cctable=cctable, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5)

# # A user can enter a course number to get its details
# @app.route('/courseselect/', methods=["GET", "POST"])
# def courseselect():
#     if request.method == "POST":
#         # Placeholder text to be displayed in courseinfo page
#         andrew = ', Welcome to Course Details'
#         # Get the course number the user selected
#         course = request.form.get("number")
#         conn = get_db_connection()
#         # Check if course number exist
#         test = conn.execute('SELECT name FROM courses WHERE number = ?', (course,)).fetchall()
#         # Get all the information of this course from each table
#         instructors = conn.execute('SELECT instructor_id FROM courses_instructors WHERE course_id = ?', (course,)).fetchall()
#         concepts = conn.execute('SELECT concept FROM courses_concepts WHERE course_id = ?', (course,)).fetchall()
#         skills = conn.execute('SELECT skill FROM courses_skills WHERE course_id = ?', (course,)).fetchall()
#         makers = conn.execute('SELECT maker FROM courses_makers WHERE course_id = ?', (course,)).fetchall()
#         ethics = conn.execute('SELECT ethic FROM courses_ethics WHERE course_id = ?', (course,)).fetchall()
#         entreps = conn.execute('SELECT entrep FROM courses_entreps WHERE course_id = ?', (course,)).fetchall()
#         prereqs = conn.execute('SELECT prereq_id FROM prereqs WHERE course_id = ?', (course,)).fetchall()
#         conn.close()
#         # If course number does not exist, render error page
#         if len(test) < 1:
#             return render_template('apology.html')
#         return render_template('courseinfo.html', andrew=andrew, course=course, concepts=concepts, instructors=instructors, skills=skills, prereqs=prereqs, makers=makers, ethics=ethics, entreps=entreps)
#     else:
#         # If this is the first time entering the page, a course number input prompt shows up.
#         return render_template("courseselect.html")
    
# # Course info page, a user can enter this page through courseselect, or jumped from other pages
# @app.route('/courseinfo/<andrew>/<course>')
# # Andrew and course are passed in from URL to generate the greeting message and course number for display
# def courseinfo(andrew, course):
#     conn = get_db_connection()
#     # Check validity
#     test = conn.execute('SELECT name FROM courses WHERE number = ?', (course,)).fetchall()
#     # Get all the information of this course from each table
#     instructors = conn.execute('SELECT instructor_id FROM courses_instructors WHERE course_id = ?', (course,)).fetchall()
#     concepts = conn.execute('SELECT concept FROM courses_concepts WHERE course_id = ?', (course,)).fetchall()
#     skills = conn.execute('SELECT skill FROM courses_skills WHERE course_id = ?', (course,)).fetchall()
#     makers = conn.execute('SELECT maker FROM courses_makers WHERE course_id = ?', (course,)).fetchall()
#     ethics = conn.execute('SELECT ethic FROM courses_ethics WHERE course_id = ?', (course,)).fetchall()
#     entreps = conn.execute('SELECT entrep FROM courses_entreps WHERE course_id = ?', (course,)).fetchall()
#     prereqs = conn.execute('SELECT prereq_id FROM prereqs WHERE course_id = ?', (course,)).fetchall()
#     conn.close()
#     if len(test) < 1:
#         return render_template('apology.html')
#     return render_template('courseinfo.html', andrew=andrew, course=course, concepts=concepts, instructors=instructors, skills=skills, prereqs=prereqs, makers=makers, ethics=ethics, entreps=entreps)

# # Error page, will be directed here if the course number/ andrew id is not in the system
# @app.route('/apology/')
# def apology():
#     return render_template('apology.html')

# # =============================================================================
# # NO LONGDER NEEDED CODE
# # @app.route('/prereq/')
# # def prereq():
# #     conn = get_db_connection()
# #     cctable = conn.execute('SELECT * FROM courses_concepts').fetchall()
# #     conn.close()
# #     return render_template('prereq.html', cctable=cctable)
# #
# # @app.route('/flowchart/')
# # def flowchart():
# #     conn = get_db_connection()
# #     cctable = conn.execute('SELECT * FROM courses_concepts').fetchall()
# #     conn.close()
# #     return render_template('flowchart.html', cctable=cctable)
# # 
# # @app.route('/allcourses/')
# # def allcourses():
# #     conn = get_db_connection()
# #     results = conn.execute('SELECT * FROM courses').fetchall()
# #     conn.close()
# #     return render_template('allcourses.html', results=results)
# # =============================================================================

# # python app.py
