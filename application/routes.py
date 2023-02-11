from application import app
from flask import render_template, url_for
import pandas as pd
import plotly
import plotly.express as px
import json
from sqlalchemy import create_engine

from pycountry_convert import country_alpha2_to_country_name, country_name_to_country_alpha3

# Connect to database and retrieve data using SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/moodle')

# 1) Calculate the number of courses/lesson (course=lesson, modules=lesson)
df_courses = pd.read_sql("SELECT * FROM mdl_course", engine)
num_courses = len(df_courses)
# q_num_lessons = """SELECT c.fullname AS course, m.name AS module, COUNT(*) as bil
# FROM mdl_course_modules cm
# INNER JOIN mdl_course c ON cm.course = c.id
# INNER JOIN mdl_modules m ON cm.module = m.id
# GROUP BY c.id, m.id"""
# df_courses = pd.read_sql(q_num_lessons, engine)
# num_courses = df_courses['bil'].sum()

# 2) Calculate the number of users
df = pd.read_sql("SELECT * FROM mdl_user", engine)
num_users = len(df)

# 3) execute the query for enrolled students/learners
query_enrolled = "SELECT COUNT(DISTINCT ue.userid) AS 'Enrolled Students' FROM mdl_user_enrolments ue"
df_enrolled = pd.read_sql(query_enrolled, engine)  # .to_string(index=False)
num_enrolled = df_enrolled['Enrolled Students'].iloc[0]

#4)

#5) total learners in each lesson
query_tlel = """
SELECT c.shortname AS 'Course Code', COUNT(DISTINCT ue.userid) AS '# of Students' 
FROM mdl_user_enrolments ue
JOIN mdl_enrol e ON ue.enrolid = e.id
JOIN mdl_course c ON e.courseid = c.id
GROUP BY e.courseid
"""
df_tlel = pd.read_sql(query_tlel, engine)
# fig1 = px.bar(df_tlel, x='Course Code', y='# of Students', title='Total Learners in Each Lesson', height=300)
# fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title=None)
# fig1.update_xaxes(showticklabels=False)
# fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0))

fig1 = px.pie(df_tlel, values='# of Students', names='Course Code', title='Total Learners in Each Lesson', height=300)
fig1.update_traces(textposition='inside', showlegend=False)
fig1.update_xaxes(showticklabels=False)
fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0))

graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

#5) new users monthly
query_usersmontly = """
SELECT DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m') AS 'Month', COUNT(*) AS 'New User'
FROM mdl_user WHERE FROM_UNIXTIME(timecreated) > '2020-01-01 00:00:00'
GROUP BY DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m')
ORDER BY timecreated DESC;
"""
df_usersmontly = pd.read_sql(query_usersmontly, engine)
fig2 = px.scatter(df_usersmontly, x='Month', y='New User', title='New Users Monthly',
                  height=300, color='New User')
fig2.update_xaxes(showticklabels=False)
fig2.update_layout(margin=dict(l=0, r=10, t=30, b=0))
graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

#6) monthly access frequency
query_accessfreq = """
SELECT DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m') AS 'Month',
       COUNT(*) AS 'Access Frequency'
FROM mdl_logstore_standard_log
GROUP BY DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m')
ORDER BY timecreated DESC;
"""
df_accessfreq = pd.read_sql(query_accessfreq, engine)
df_accessfreq['Month'] = pd.to_datetime(df_accessfreq['Month'], format='%Y-%m')

fig3 = px.scatter(df_accessfreq, x='Month', y='Access Frequency', title='Monthly Access Frequency', height=300, trendline="ols")
fig3.update_xaxes(showticklabels=False)
fig3.update_layout(margin=dict(l=0, r=10, t=30, b=0))
graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

#7) users' country
query_usercountry = "SELECT country, COUNT(*) AS count FROM mdl_user GROUP BY country"
df_usercountry = pd.read_sql(query_usercountry, engine)
# Create a plotly choropleth map of users' countries
fig_map = px.choropleth(df_usercountry, locations="country", color="count",
                        color_discrete_sequence=px.colors.sequential.Plasma,
                        title='Map Country of Users')
fig_map.update_layout(margin=dict(l=0, r=10, t=30, b=0))
graph4JSON = json.dumps(fig_map, cls=plotly.utils.PlotlyJSONEncoder)

@app.route("/")
def index():
    return render_template(
        'index.html',
        title='Home',
        graph1JSON=graph1JSON,
        graph2JSON=graph2JSON,
        graph3JSON=graph3JSON,
        graph4JSON=graph4JSON,
        num_users=num_users,
        num_courses=num_courses,
        num_enrolled=num_enrolled
    )
