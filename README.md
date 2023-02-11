# Moodle Dashboard for Cassmile Insights
This code is a Python Flask application that provides a dashboard for monitoring and analyzing various statistics related to a Moodle e-learning platform.

The dashboard includes:

- Total number of courses/lessons
- Total number of registered users
- Total number of enrolled students/learners
- A pie chart showing the total number of learners in each course/lesson
- A scatter plot showing the monthly count of new user registration
- A scatter plot showing the monthly access frequency to the platform
- A choropleth map showing the number of users in each country

Note: The data is extracted from a MySQL database using SQLAlchemy and processed using pandas library. The charts are generated using Plotly and are rendered as JSON objects in the Flask application.

Usage
To use the Moodle Dashboard, follow these steps:

- Install the required dependencies by running pip install -r requirements.txt
- Connect to your Moodle MySQL database by modifying the create_engine function in the code with your credentials
- Run the Flask application by running the command flask run in your terminal
- Access the dashboard by visiting http://localhost:5000 in your web browser
- On the dashboard page, you can view the various charts and switch between yearly, quarterly or monthly views.
