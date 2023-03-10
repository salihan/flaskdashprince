from application import app
from flask import render_template, url_for, jsonify, render_template, request
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from sqlalchemy import create_engine
from plotly.subplots import make_subplots


# Connect to database and retrieve data using SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/cassmile')


@app.route("/")
def index():
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

    # 4)

    # 5) total learners in each lesson
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

    # fig1 = px.pie(df_tlel, values='# of Students', names='Course Code', title='Total Learners in Each Lesson',
    #               height=200)
    # fig1.update_traces(textposition='inside', showlegend=False)
    # fig1.update_xaxes(showticklabels=False)
    # fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))

    # pivot the data to create a matrix
    # matrix = pd.pivot_table(df_tlel, values="# of Students", index=["Course Code"], columns=[])
    # # plot the heatmap using Plotly
    # fig1 = px.imshow(matrix, x=matrix.columns, y=matrix.index)

    # treemap
    fig1 = px.treemap(df_tlel, path=['Course Code'], values='# of Students', title='Total Learners in Each Lesson',
                  height=200)
    fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0))

    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # 6) new users monthly
    query_usersmontly = """
    SELECT year, month, day, COUNT(*) AS 'New User'
    FROM mdl_user WHERE year > 2019
    GROUP BY month
    ORDER BY timecreated DESC;
    """
    df_usersmontly = pd.read_sql(query_usersmontly, engine)
    fig2 = px.scatter(df_usersmontly, x='month', y='New User', title='New Users Monthly',
                      height=200, color='New User', hover_data=['year', 'day'])
    fig2.update_xaxes(showticklabels=False)
    fig2.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    # xaxis=dict(rangeslider=dict(visible=True)))
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # 7) monthly access frequency
    query_accessfreq = """
    SELECT year, month, day, COUNT(*) AS 'Access Frequency'
    FROM mdl_logstore_standard_log
    GROUP BY month
    ORDER BY timecreated DESC;
    """
    df_accessfreq = pd.read_sql(query_accessfreq, engine)
    # df_accessfreq['Month'] = pd.to_datetime(df_accessfreq['Month'], format='%Y-%m')

    fig3 = px.scatter(df_accessfreq, x='month', y='Access Frequency', title='Monthly Access Frequency', height=200,
                      trendline="ols", hover_data=['year', 'day'])
    fig3.update_xaxes(showticklabels=False)
    fig3.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # 8) users' country
    query_usercountry = "SELECT country, COUNT(*) AS count FROM mdl_user GROUP BY country"
    df_usercountry = pd.read_sql(query_usercountry, engine)

    # percubaan choropleth
    # fig_map = px.choropleth(df_usercountry, locations="country", color="count",
    #                         color_continuous_scale='Inferno',
    #                         scope='world',
    #                         projection='equirectangular')
    # fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))

    # percubaan entah kali ke-berapa
    # fig_map = go.Figure(data=go.Choropleth(
    #     locations=df_usercountry['country'],
    #     z=df_usercountry['count'],
    #     colorscale='Inferno',
    #     autocolorscale=False,
    #     reversescale=True,
    #     colorbar=dict(
    #         x=0,
    #         y=0.5,
    #         len=0.5,
    #         orientation='h',
    #         title='Users Count'
    #     ),
    # ))
    # # update layout
    # fig_map.update_layout(
    #     width=600,
    #     geo=dict(
    #         showframe=False,
    #         showcoastlines=False,
    #         projection_type='equirectangular'
    #     ),
    #     margin=dict(t=0, b=0, l=0, r=0),
    #     paper_bgcolor='rgba(0,0,0,0)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    # )

    # ---------- percubaan utk scattermapbox --------------
    # I found the useful file and lets use it
    loc_df = pd.read_csv('application/static/countries_codes_and_coordinates.csv')
    # dlm file ni ada character yg tak diingini. lets remove it
    loc_df.replace('"', '', regex=True, inplace=True)
    # Join the two DataFrames on the Alpha-3 code column. But first, lets remove unwanted spaces
    loc_df['Alpha-3 code'] = loc_df['Alpha-3 code'].str.strip()
    joined_df = df_usercountry.merge(loc_df, left_on='country', right_on='Alpha-3 code')
    # rename columns names to follow the standard
    joined_df = joined_df.rename(columns={'count': 'user_count', 'Alpha-3 code': 'iso3', 'Latitude (average)': 'lat',
                                          'Longitude (average)': 'lon'})
    # I dunno why I have to do this.. last time it was error. SO..
    # Convert lat and lon columns to string datatype
    joined_df['lat'] = joined_df['lat'].astype(str)
    joined_df['lon'] = joined_df['lon'].astype(str)
    # Convert lat and lon values to float
    joined_df['lat'] = joined_df['lat'].apply(lambda x: float(x))
    joined_df['lon'] = joined_df['lon'].apply(lambda x: float(x))
    #lastly, make the scattermap
    fig_map = px.scatter_mapbox(joined_df, lat="lat", lon="lon", hover_name="Country", hover_data=["user_count"], zoom=1,
                            color="user_count", size="user_count")
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(t=0, b=0, l=0, r=0), height=300)


    # ---------- end scattermapbox ------------------------


    graph4JSON = json.dumps(fig_map, cls=plotly.utils.PlotlyJSONEncoder)


    #9) Badges
    query_badges = """
        SELECT b.name, COUNT(DISTINCT(bcm.userid)) AS bil
        FROM mdl_badge_criteria_met bcm
        INNER JOIN mdl_badge_criteria bc ON bcm.critid = bc.id
        INNER JOIN mdl_badge b ON bc.badgeid = b.id
        WHERE bcm.issuedid IS NOT null
        GROUP BY b.name
        ORDER BY bil DESC
        LIMIT 6"""
    df_topbadges = pd.read_sql(query_badges, engine)
    # print(df_topbadges.at[0,'name'])
    # fig_badge1 = go.Figure(go.Indicator(
    #     domain={'x': [0, 1], 'y': [0, 1]},
    #     value=450,
    #     mode="gauge+number+delta",
    #     title={'text': "Speed"},
    #     delta={'reference': 380},
    #     gauge={'axis': {'range': [None, 500]},
    #            'steps': [
    #                {'range': [0, 250], 'color': "lightgray"},
    #                {'range': [250, 400], 'color': "gray"}],
    #            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}}))
    #
    # gauge1JSON = json.dumps(fig_badge1, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'index.html',
        title='Home',
        graph1JSON=graph1JSON,
        graph2JSON=graph2JSON,
        graph3JSON=graph3JSON,
        graph4JSON=graph4JSON,
        # gauge1JSON=gauge1JSON,
        df_topbadges=df_topbadges,
        num_users=num_users,
        num_courses=num_courses,
        num_enrolled=num_enrolled
    )

@app.route('/dashboard1', methods=['GET', 'POST'])
def dashboard1():
    if request.method == 'POST':

        # Get selected date range from date slider
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Filter the data by the selected date range
        query = "SELECT * FROM mdl_logstore_standard_log WHERE timecreated BETWEEN %s AND %s"
        data = pd.read_sql_query(query, engine, params=[start_date, end_date])

    else:

        # Get the start and end dates from the log table
        query = "SELECT MIN(timecreated) AS start_date, MAX(timecreated) AS end_date FROM mdl_logstore_standard_log;"
        result = engine.execute(query).fetchone()
        start_date = result[0].strftime('%Y-%m-%d')
        end_date = result[1].strftime('%Y-%m-%d')

    # 1) Calculate the number of courses/lesson (course=lesson, modules=lesson)
    query1 = "SELECT * FROM mdl_course where timecreated BETWEEN %s AND %s"
    num_courses = len(pd.read_sql_query(query1, engine, params=[start_date, end_date]))

    # 2) Calculate the number of users
    query2 = "SELECT * FROM mdl_user where timecreated BETWEEN %s AND %s"
    num_users = len(pd.read_sql(query2, engine, params=[start_date, end_date]))

    # 3) execute the query for enrolled students/learners
    query_enrolled = "SELECT COUNT(DISTINCT ue.userid) AS 'Enrolled Students' FROM mdl_user_enrolments ue where FROM_UNIXTIME(timecreated, '%%Y-%%m-%%d') BETWEEN %s AND %s"
    df_enrolled = pd.read_sql(query_enrolled, engine, params=[start_date, end_date])
    num_enrolled = df_enrolled['Enrolled Students'].iloc[0]

    #4) Cert - find the count of certified per not yet complete
    query_certified = """
        SELECT (
            SELECT COUNT(cmc.id) FROM mdl_course_modules_completion cmc
                INNER JOIN mdl_course_modules cm ON cmc.coursemoduleid = cm.id
                INNER JOIN mdl_modules m ON cm.module = m.id
                WHERE (cm.module = 24 OR cm.module = 14) 
                    AND cmc.completionstate > 0 
                    AND cmc.timemodified BETWEEN %s AND %s ) 
        + ( SELECT COUNT(id) FROM mdl_customcert_issues ) AS cert
    """
    query_belumcertify = """
        SELECT (
            SELECT COUNT(cmc.id) FROM mdl_course_modules_completion cmc
                INNER JOIN mdl_course_modules cm ON cmc.coursemoduleid = cm.id
                INNER JOIN mdl_modules m ON cm.module = m.id
                WHERE (cm.module = 24 OR cm.module = 14) 
                    AND cmc.timemodified BETWEEN %s AND %s ) 
        + ( SELECT COUNT(id) FROM mdl_customcert_issues ) AS cert
    """
    df_certified = pd.read_sql(query_certified, engine, params=[start_date, end_date])
    df_belumcertify = pd.read_sql(query_belumcertify, engine, params=[start_date, end_date])
    num_certified = df_certified['cert'].iloc[0]
    num_belumcertify = df_belumcertify['cert'].iloc[0]
    certified_percent = round((num_certified / num_belumcertify) * 100, 2)

    # 5) total learners in each lesson
    query_tlel = """
        SELECT c.shortname AS 'Course Code', COUNT(DISTINCT ue.userid) AS '# of Students' 
        FROM mdl_user_enrolments ue 
        JOIN mdl_enrol e ON ue.enrolid = e.id
        JOIN mdl_course c ON e.courseid = c.id
        where FROM_UNIXTIME(ue.timecreated, '%%Y-%%m-%%d') BETWEEN %s AND %s
        GROUP BY e.courseid
        """
    df_tlel = pd.read_sql(query_tlel, engine, params=[start_date, end_date])
    # treemap
    fig1 = px.treemap(df_tlel, path=['Course Code'], values='# of Students', title='Total Learners in Each Lesson', height=200)
    fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0))
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # 6) new users monthly
    query_usersmontly = """
        SELECT timecreated_year, timecreated_month as 'Month', timecreated_day, COUNT(*) AS 'New User'
        FROM mdl_user WHERE timecreated BETWEEN %s AND %s
        GROUP BY timecreated_month
        ORDER BY timecreated_year DESC, timecreated_month DESC, timecreated_day DESC;
        """
    df_usersmontly = pd.read_sql(query_usersmontly, engine, params=[start_date, end_date])
    fig2 = px.scatter(df_usersmontly, x='Month', y='New User', title='New Users Monthly',
                      height=200, color='New User', hover_data=['timecreated_year', 'timecreated_day'])
    fig2.update_xaxes(showticklabels=False)
    fig2.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    # xaxis=dict(rangeslider=dict(visible=True)))
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # 7) monthly access frequency
    query_accessfreq = """
        SELECT year, month, day, COUNT(*) AS 'Access Frequency'
        FROM mdl_logstore_standard_log WHERE timecreated BETWEEN %s AND %s
        GROUP BY month
        ORDER BY year DESC, month DESC, day DESC;
        """
    df_accessfreq = pd.read_sql(query_accessfreq, engine, params=[start_date, end_date])
    fig3 = px.scatter(df_accessfreq, x='month', y='Access Frequency', title='Monthly Access Frequency', height=200,
                      trendline="ols", hover_data=['year', 'day'])
    fig3.update_xaxes(showticklabels=False)
    fig3.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # 8) Badges
    query_badges = """
            SELECT b.name, COUNT(DISTINCT(bcm.userid)) AS bil
            FROM mdl_badge_criteria_met bcm
            INNER JOIN mdl_badge_issued bi ON bcm.issuedid=bi.id
            INNER JOIN mdl_badge_criteria bc ON bcm.critid = bc.id
            INNER JOIN mdl_badge b ON bc.badgeid = b.id
            WHERE bcm.issuedid IS NOT null AND bi.dateissued BETWEEN %s AND %s
            GROUP BY b.name
            ORDER BY bil DESC
            LIMIT 6"""
    df_topbadges = pd.read_sql(query_badges, engine, params=[start_date, end_date])

    # 9) users' country
    query_usercountry = """SELECT country, COUNT(*) AS count FROM mdl_user 
                        WHERE timecreated BETWEEN %s AND %s GROUP BY country"""
    df_usercountry = pd.read_sql(query_usercountry, engine, params=[start_date, end_date])
    fig_map = usermap(df_usercountry)
    graph4JSON = json.dumps(fig_map, cls=plotly.utils.PlotlyJSONEncoder)


    # Render the dashboard template
    return render_template('dashboard1.html',
                           start_date=start_date, end_date=end_date,
                           num_courses=num_courses,
                           num_users=num_users,
                           num_enrolled=num_enrolled,
                           num_certified=num_certified, num_belumcertify=num_belumcertify, certified_percent=certified_percent,
                           graph1JSON=graph1JSON,
                           graph2JSON=graph2JSON,
                           graph3JSON=graph3JSON,
                           df_topbadges=df_topbadges,
                           graph4JSON=graph4JSON)


@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():
    courses_list = []
    selected_course = 0
    if request.method == 'GET':
        # Get the start and end dates from the log table
        query = "SELECT MIN(timecreated) AS start_date, MAX(timecreated) AS end_date FROM mdl_logstore_standard_log;"
        result = engine.execute(query).fetchone()
        start_date = result[0].strftime('%Y-%m-%d')
        end_date = result[1].strftime('%Y-%m-%d')

        # Get list of course titles from the database
        query_courses = "SELECT DISTINCT fullname, id FROM mdl_course where timecreated BETWEEN %s AND %s ORDER BY fullname ASC;"
        courses_df = pd.read_sql(query_courses, con=engine, params=[start_date, end_date])
        # courses = courses_df['fullname'].tolist()
        courses_list = [(row['fullname'], row['id']) for _, row in courses_df.iterrows()]

        # Set default course to the first one in the list
        default_course = courses_list[0][1]
        selected_course = str(default_course)
        # print(courses_list[0][0])

    else:
        # Get selected date range from date slider
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        selected_course = request.form.get('course-selector', default='1', type=str)
        # selected_course = request.form['course-selector']

        # Get list of course titles from the database
        query_courses = "SELECT DISTINCT fullname, id FROM mdl_course where timecreated BETWEEN %s AND %s ORDER BY fullname ASC;"
        courses_df = pd.read_sql(query_courses, con=engine, params=(start_date, end_date))
        # courses = courses_df['fullname'].tolist()
        courses_list = [(row['fullname'], row['id']) for _, row in courses_df.iterrows()]

    # 1) execute the query for enrolled students/learners
    query_enrolled = """SELECT COUNT(DISTINCT ue.userid) AS 'Enrolled' 
        FROM mdl_user_enrolments ue INNER JOIN mdl_enrol e ON ue.enrolid = e.id 
        where e.courseid = %s AND FROM_UNIXTIME(ue.timecreated, '%%Y-%%m-%%d') BETWEEN %s AND %s"""
    df_enrolled = pd.read_sql(query_enrolled, engine, params=(selected_course, start_date, end_date))
    num_enrolled = df_enrolled['Enrolled'].iloc[0]
    print("selected_course: "+selected_course)

    # 2) Cert
    query_certified = """
                    SELECT ( SELECT COUNT(cmc.id) FROM mdl_course_modules_completion cmc
                            INNER JOIN mdl_course_modules cm ON cmc.coursemoduleid = cm.id
                            INNER JOIN mdl_modules m ON cm.module = m.id
                            WHERE (cm.module = 24 OR cm.module = 14) 
                                AND cmc.completionstate > 0 
                                AND cmc.timemodified BETWEEN %s AND %s 
                                AND cm.course = %s ) +
                ( SELECT COUNT(cci.id) FROM mdl_customcert_issues cci
                    INNER JOIN mdl_customcert cc ON cci.customcertid = cc.id
                    WHERE cc.course = 229 ) AS cert
            """
    df_certified = pd.read_sql(query_certified, engine, params=(start_date, end_date, selected_course))
    num_certified = df_certified['cert'].iloc[0]

    # 3) Badges
    query_badges = """ SELECT b.name, COUNT(DISTINCT(bcm.userid)) AS bil
        FROM mdl_badge_criteria_met bcm
        INNER JOIN mdl_badge_issued bi ON bcm.issuedid=bi.id
        INNER JOIN mdl_badge_criteria bc ON bcm.critid = bc.id
        INNER JOIN mdl_badge b ON bc.badgeid = b.id
        WHERE bcm.issuedid IS NOT NULL AND b.courseid = %s """
    df_badges = pd.read_sql(query_badges, engine, params=(selected_course,))
    num_badges = df_badges['bil'].iloc[0]
    # print(df_badges)

    # 5) watch
    query_watch = """ select shortname, userid, count(distinct(userid)) as 'count_users' from watch 
                where timecreated BETWEEN %s AND %s AND courseid = %s """
    df_watch = pd.read_sql(query_watch, engine, params=(start_date, end_date, selected_course))
    num_watch = df_watch['count_users'].iloc[0]

    # 6) reflect
    query_reflect = """  SELECT c.shortname, u.id as userid, count(u.id) AS total_reflect
                    FROM mdl_quiz q                    
                    inner JOIN mdl_quiz_grades qg ON q.id = qg.quiz
                    inner JOIN mdl_course c ON q.course = c.id
                    inner JOIN mdl_user u ON qg.userid = u.id
                    where q.timecreated BETWEEN %s AND %s AND c.id = %s """
    df_reflect = pd.read_sql(query_reflect, engine, params=(start_date, end_date, selected_course))
    num_reflect = df_reflect['total_reflect'].iloc[0]

    # 7) digfurther
    query_digfurther = """  SELECT p.name, c.shortname, COUNT(p.id) AS digfurther
                        FROM mdl_page p 
                        INNER JOIN mdl_course c ON c.id = p.course                        
                        where p.timemodified BETWEEN %s AND %s AND c.id = %s """
    df_digfurther = pd.read_sql(query_digfurther, engine, params=(start_date, end_date, selected_course))
    num_digfurther = df_digfurther['digfurther'].iloc[0]

    # 8) uLesson
    num_ulesson = 0
    if not df_digfurther.empty:
        df_ulesson = df_digfurther[df_digfurther['name'].str.contains('Lesson', na=False)]
        if not df_ulesson.empty:
            num_ulesson = df_ulesson['digfurther'].iloc[0]

    # 9) user map
    query_usercountry2 = """SELECT u.country, COUNT(u.id) AS count FROM mdl_user u
                            inner join mdl_user_enrolments ue on u.id = ue.userid
                            INNER JOIN mdl_enrol e ON ue.enrolid = e.id
                            WHERE u.timecreated BETWEEN %s AND %s AND e.courseid = %s
                            GROUP BY country"""

    df_usercountry2 = pd.read_sql(query_usercountry2, engine, params=(start_date, end_date, selected_course))
    fig_map = usermap(df_usercountry2)
    graph4JSON = json.dumps(fig_map, cls=plotly.utils.PlotlyJSONEncoder)

    # 10) enrolled date
    query_enrolleddate = """SELECT ue.userid, u.email, FROM_UNIXTIME(ue.timecreated, '%%Y-%%m-%%d') AS 'Enrolled Date' 
                        FROM mdl_user_enrolments ue 
                        INNER JOIN mdl_enrol e ON ue.enrolid = e.id 
                        INNER JOIN mdl_user u ON ue.userid = u.id
                        WHERE FROM_UNIXTIME(ue.timecreated, '%%Y-%%m-%%d') BETWEEN %s AND %s AND e.courseid = %s"""
    df_enrolleddate = pd.read_sql(query_enrolleddate, engine, params=(start_date, end_date, selected_course))

    # Create the table trace
    table_trace = go.Table(
        header=dict(values=['User ID', 'Email', 'Enrolled Date']),
        cells=dict(values=[df_enrolleddate['userid'], df_enrolleddate['email'], df_enrolleddate['Enrolled Date']])
    )

    # Convert the table trace to JSON
    table_data = [table_trace.to_plotly_json()]
    table_data = json.dumps(table_data)

    # 11) new users monthly based on selected course
    query_newusers_oncourse = """
                        SELECT u.timecreated_year, u.timecreated_month as 'Month', u.timecreated_day, COUNT(u.id) AS 'New User'
                        FROM mdl_user u 
                        INNER JOIN mdl_user_enrolments ue ON u.id = ue.userid
                        INNER JOIN mdl_enrol e ON ue.enrolid = e.id
                        WHERE u.timecreated BETWEEN %s AND %s AND e.courseid = %s
                        GROUP BY u.timecreated_month
                        ORDER BY u.timecreated_year DESC, u.timecreated_month DESC, u.timecreated_day DESC"""
    df_newusers_oncourse = pd.read_sql(query_newusers_oncourse, engine, params=(start_date, end_date, selected_course))
    fig_newusers_oncourse = px.scatter(df_newusers_oncourse, x='Month', y='New User', title='New Users Monthly',
                      height=200, color='New User', hover_data=['timecreated_year', 'timecreated_day'])
    fig_newusers_oncourse.update_xaxes(showticklabels=False)
    fig_newusers_oncourse.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    newusers_oncourse_JSON = json.dumps(fig_newusers_oncourse, cls=plotly.utils.PlotlyJSONEncoder)

    # 12) monthly access frequency based on selected course
    query_accessfreq = """
            SELECT year, month, day, COUNT(*) AS 'Access Frequency'
            FROM mdl_logstore_standard_log WHERE timecreated BETWEEN %s AND %s AND courseid = %s
            GROUP BY month
            ORDER BY year DESC, month DESC, day DESC;
            """
    df_accessfreq = pd.read_sql(query_accessfreq, engine, params=[start_date, end_date, selected_course])
    fig3 = px.scatter(df_accessfreq, x='month', y='Access Frequency', title='Monthly Access Frequency', height=200,
                      trendline="ols", hover_data=['year', 'day'])
    fig3.update_xaxes(showticklabels=False)
    fig3.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    monthly_access_JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # ------ render -----------

    return render_template('dashboard2.html',
                           start_date=start_date, end_date=end_date,
                           courses=courses_list, selected_course=selected_course,
                           num_enrolled=num_enrolled,
                           num_certified=num_certified,
                           num_badges=num_badges,
                           num_watch=num_watch,
                           num_reflect=num_reflect,
                           num_digfurther=num_digfurther,
                           num_ulesson=num_ulesson,
                           graph4JSON=graph4JSON,
                           table_data=table_data,
                           newusers_oncourse_JSON=newusers_oncourse_JSON,
                           monthly_access_JSON=monthly_access_JSON)



@app.route('/test2')
def test2():
    # define SQL query and read data into a pandas dataframe
    query_tlel = """
    SELECT DATE(FROM_UNIXTIME(ue.timecreated)) AS 'Time_Created', c.shortname AS 'Course Code', COUNT(DISTINCT ue.userid) AS 'Number of Students' 
    FROM mdl_user_enrolments ue
    JOIN mdl_enrol e ON ue.enrolid = e.id
    JOIN mdl_course c ON e.courseid = c.id
    GROUP BY e.courseid
    """
    df_tlel = pd.read_sql(query_tlel, engine)

    # create figure with Plotly
    fig_test2 = px.bar(df_tlel, x='Time_Created', y='Number of Students', color='Course Code')
    # fig1 = px.bar(df_tlel, x='Course Code', y='# of Students', title='Total Learners in Each Lesson', height=300)
    # fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title=None)
    # fig1.update_xaxes(showticklabels=False)
    # fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0))

    # add a range slider to the figure
    # fig_test2.update_layout(xaxis_rangeslider_visible=True)
    fig_test2.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    graphTest2JSON = json.dumps(fig_test2, cls=plotly.utils.PlotlyJSONEncoder)

    # return the figure as a JSON object and render it in the HTML template
    return render_template('test2.html', graphTest2JSON=graphTest2JSON)



@app.route('/test3')
def test3():
    # retrieve data from Moodle 4.0 PhpMyAdmin using SQLAlchemy
    df_test3 = pd.read_sql_query(
        "SELECT c.shortname AS 'Course Code', COUNT(DISTINCT ue.userid) AS '# of Students' FROM mdl_user_enrolments ue JOIN mdl_enrol e ON ue.enrolid = e.id JOIN mdl_course c ON e.courseid = c.id GROUP BY e.courseid",
        engine)

    # create a Plotly bar chart
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=df_test3['Course Code'], y=df_test3['# of Students']),
        row=1, col=1
    )
    fig.update_layout(title='Total Learners in Each Lesson')
    plot_div = fig.to_html(full_html=False)

    # create a table of the data
    table = df_test3.to_html(classes='table table-striped')

    # get the minimum and maximum date from the data
    df_test3["log_date"] = pd.to_datetime(df_test3["timecreated"])
    df_test3["log_date_unix"] = df_test3["log_date"].apply(lambda x: x.timestamp())
    min_date = df_test3["log_date_unix"].min()
    max_date = df_test3["log_date_unix"].max()
    print(min_date)
    print(max_date)

    return render_template('test3.html', plot_div=plot_div, table=table, min_date=min_date, max_date=max_date)


def usermap(dfcountry):
    # ---------- percubaan utk scattermapbox --------------
    # I found the useful file and lets use it
    loc_df = pd.read_csv('application/static/countries_codes_and_coordinates.csv')
    # dlm file ni ada character yg tak diingini. lets remove it
    loc_df.replace('"', '', regex=True, inplace=True)
    # Join the two DataFrames on the Alpha-3 code column. But first, lets remove unwanted spaces
    loc_df['Alpha-3 code'] = loc_df['Alpha-3 code'].str.strip()
    joined_df = dfcountry.merge(loc_df, left_on='country', right_on='Alpha-3 code')
    # rename columns names to follow the standard
    joined_df = joined_df.rename(columns={'count': 'user_count', 'Alpha-3 code': 'iso3', 'Latitude (average)': 'lat',
                                          'Longitude (average)': 'lon'})
    # I dunno why I have to do this.. last time it was error. so.. buat je la
    # Convert lat and lon columns to string datatype
    joined_df['lat'] = joined_df['lat'].astype(str)
    joined_df['lon'] = joined_df['lon'].astype(str)
    # Convert lat and lon values to float
    joined_df['lat'] = joined_df['lat'].apply(lambda x: float(x))
    joined_df['lon'] = joined_df['lon'].apply(lambda x: float(x))
    # lastly, make the scattermap
    fig_map = px.scatter_mapbox(joined_df, lat="lat", lon="lon", hover_name="Country", hover_data=["user_count"],
                                zoom=1.5, color="user_count", size="user_count")
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(t=0, b=0, l=0, r=0), height=300)
    return fig_map
    # ---------- end scattermapbox ------------------------