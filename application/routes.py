from application import app
from flask import render_template, url_for, jsonify, render_template, request
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from sqlalchemy import create_engine

from plotly.subplots import make_subplots
from datetime import datetime

# Connect to database and retrieve data using SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/moodle')


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

    fig1 = px.pie(df_tlel, values='# of Students', names='Course Code', title='Total Learners in Each Lesson',
                  height=200)
    fig1.update_traces(textposition='inside', showlegend=False)
    fig1.update_xaxes(showticklabels=False)
    fig1.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))

    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # 6) new users monthly
    query_usersmontly = """
    SELECT DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m') AS 'Month', COUNT(*) AS 'New User'
    FROM mdl_user WHERE FROM_UNIXTIME(timecreated) > '2020-01-01 00:00:00'
    GROUP BY DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m')
    ORDER BY timecreated DESC;
    """
    df_usersmontly = pd.read_sql(query_usersmontly, engine)
    fig2 = px.scatter(df_usersmontly, x='Month', y='New User', title='New Users Monthly',
                      height=200, color='New User', color_continuous_scale='Bluered_r')
    fig2.update_xaxes(showticklabels=False)
    fig2.update_layout(margin=dict(l=0, r=10, t=30, b=0), font=dict(size=10, color="RebeccaPurple"))
    # xaxis=dict(rangeslider=dict(visible=True)))
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # 7) monthly access frequency
    query_accessfreq = """
    SELECT DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m') AS 'Month',
           COUNT(*) AS 'Access Frequency'
    FROM mdl_logstore_standard_log
    GROUP BY DATE_FORMAT(FROM_UNIXTIME(timecreated), '%%Y-%%m')
    ORDER BY timecreated DESC;
    """
    df_accessfreq = pd.read_sql(query_accessfreq, engine)
    df_accessfreq['Month'] = pd.to_datetime(df_accessfreq['Month'], format='%Y-%m')

    fig3 = px.scatter(df_accessfreq, x='Month', y='Access Frequency', title='Monthly Access Frequency', height=200,
                      trendline="ols")
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
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(t=0, b=0, l=0, r=0))


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