
import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io
import plotly.express as px
from geopy.geocoders import Nominatim
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from Courses import (
    ds_course, web_course, android_course,
    ios_course, uiux_course, resume_videos, interview_videos
)

import nltk
nltk.download('stopwords')

from Courses import (
    course_recommender,
    ds_course,
    web_course,
    android_course,
    ios_course,
    uiux_course,
    resume_videos,
    interview_videos
)


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',    
    db='cv'
)
cursor = connection.cursor()


def get_safe_location():
    """
    Prevents crash when geocoder or Nominatim fails.
    Always returns: city, state, country, latlong
    """
    try:
        g = geocoder.ip("me")
        latlong = g.latlng
    except:
        return "Unknown", "Unknown", "Unknown", None

    if not latlong:
        return "Unknown", "Unknown", "Unknown", None

    try:
        geolocator = Nominatim(user_agent="resume_app")
        location = geolocator.reverse(latlong, language='en', timeout=10)
        if location and "address" in location.raw:
            addr = location.raw["address"]
            city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
            state = addr.get("state", "Unknown")
            country = addr.get("country", "Unknown")
            return city, state, country, latlong
    except:
        return "Unknown", "Unknown", "Unknown", latlong

    return "Unknown", "Unknown", "Unknown", latlong


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="./Logo/recommend.png"
)


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(file, "rb") as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            interpreter.process_page(page)

    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_csv_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'


def run():


    try:
        img = Image.open("./Logo/RESUM.png")
        st.image(img)
    except:
        st.error("❌ RESUM.png not found in ./Logo/")

    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    link = """
    <b>Built with 🤍 by 
    <a href="https://dnoobnerd.netlify.app/" style="text-decoration: none; color: #021659;">
    Aditya Agrawal</a></b>
    """
    st.sidebar.markdown(link, unsafe_allow_html=True)

    st.sidebar.markdown("""
        <p>Visitors 
        <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" 
        width="60px"/></p>
    """, unsafe_allow_html=True)

    
    cursor.execute("CREATE DATABASE IF NOT EXISTS cv;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            ID INT NOT NULL AUTO_INCREMENT,
            sec_token VARCHAR(20),
            ip_add VARCHAR(50),
            host_name VARCHAR(50),
            dev_user VARCHAR(50),
            os_name_ver VARCHAR(50),
            latlong VARCHAR(50),
            city VARCHAR(50),
            state VARCHAR(50),
            country VARCHAR(50),
            act_name VARCHAR(50),
            act_mail VARCHAR(50),
            act_mob VARCHAR(20),
            Name VARCHAR(500),
            Email_ID VARCHAR(500),
            resume_score VARCHAR(8),
            Timestamp VARCHAR(50),
            Page_no VARCHAR(5),
            Predicted_Field BLOB,
            User_level BLOB,
            Actual_skills BLOB,
            Recommended_skills BLOB,
            Recommended_courses BLOB,
            pdf_name VARCHAR(50),
            PRIMARY KEY (ID)
        );
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            ID INT NOT NULL AUTO_INCREMENT,
            feed_name VARCHAR(50),
            feed_email VARCHAR(50),
            feed_score VARCHAR(5),
            comments VARCHAR(100),
            Timestamp VARCHAR(50),
            PRIMARY KEY (ID)
        );
    """)

    if choice == "User":

        st.header("User Panel")

        act_name = st.text_input("Name*")
        act_mail = st.text_input("Mail*")
        act_mob = st.text_input("Mobile Number*")

      
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()

        city, state, country, latlong = get_safe_location()

        st.markdown(
            "<h5 style='color:#021659;'>Upload resume for analysis</h5>",
            unsafe_allow_html=True
        )

        pdf_file = st.file_uploader("Choose your resume", type=["pdf"])
        if pdf_file is not None:

            with st.spinner("Analyzing your resume..."):
                time.sleep(3)

            save_path = "./Uploaded_Resumes/" + pdf_file.name
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            show_pdf(save_path)

          
            resume_data = ResumeParser(save_path).get_extracted_data()
            resume_text = pdf_reader(save_path)
            if resume_data:

                st.header("Resume Analysis 🤘")
                st.success("Hello " + str(resume_data.get("name", "User")))
                st.subheader("Your Basic Info")

                st.text("Name: " + str(resume_data.get("name")))
                st.text("Email: " + str(resume_data.get("email")))
                st.text("Contact: " + str(resume_data.get("mobile_number")))
                st.text("Degree: " + str(resume_data.get("degree")))
                st.text("Pages: " + str(resume_data.get("no_of_pages")))

     
                st.subheader("Experience Level Prediction")

                cand_level = "Fresher"

                text = resume_text.upper()

                if "INTERNSHIP" in text:
                    cand_level = "Intermediate"
                    st.success("Intermediate Level detected (Internship found)")
                elif "EXPERIENCE" in text or "WORK EXPERIENCE" in text:
                    cand_level = "Experienced"
                    st.success("Experienced Level detected")
                else:
                    st.info("Fresher Level detected")

          
                st.subheader("Skills Recommendation 💡")

                resume_skills = resume_data.get("skills", [])

                st_tags(
                    label="Your Current Skills:",
                    text="Detected from your resume",
                    value=resume_skills,
                    key="current-skills"
                )

                # Keyword categories
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node js', 'php', 'wordpress','javascript','angular']
                android_keyword = ['android','kotlin','flutter','xml']
                ios_keyword = ['ios','swift','xcode']
                uiux_keyword = ['ui','ux','figma','adobe xd','wireframes']
                gen_keyword = ['english','communication','leadership']

                reco_field = "NA"
                recommended_skills = []
                rec_course = []

                # Classification based on skills
                for skill in resume_skills:
                    s = skill.lower()

                    if s in ds_keyword:
                        reco_field = "Data Science"
                        recommended_skills = ['TensorFlow','Pytorch','Web Scraping','ML Algorithms','Statistics']
                        rec_course = course_recommender(ds_course)
                        st.success("Field: Data Science")
                        break

                    elif s in web_keyword:
                        reco_field = "Web Development"
                        recommended_skills = ['React','Django','NodeJS','REST APIs']
                        rec_course = course_recommender(web_course)
                        st.success("Field: Web Development")
                        break

                    elif s in android_keyword:
                        reco_field = "Android Development"
                        recommended_skills = ['Kotlin','Android Studio','Firebase']
                        rec_course = course_recommender(android_course)
                        st.success("Field: Android Development")
                        break

                    elif s in ios_keyword:
                        reco_field = "IOS Development"
                        recommended_skills = ['Swift','SwiftUI','Cocoa Touch']
                        rec_course = course_recommender(ios_course)
                        st.success("Field: iOS Development")
                        break

                    elif s in uiux_keyword:
                        reco_field = "UI/UX"
                        recommended_skills = ['Wireframing','User Research','Prototyping']
                        rec_course = course_recommender(uiux_course)
                        st.success("Field: UI/UX Design")
                        break

                    elif s in gen_keyword:
                        reco_field = "NA"
                        recommended_skills = ["General Soft Skills"]
                        st.warning("Only general skills detected")
                        break

                st_tags(
                    label="Recommended Skills:",
                    text="Add these to improve your resume",
                    value=recommended_skills,
                    key="recommended-skills"
                )

                st.subheader("Resume Score 📝")

                resume_score = 0
                rules = {
                    "OBJECTIVE": 6,
                    "SUMMARY": 6,
                    "EDUCATION": 12,
                    "EXPERIENCE": 16,
                    "INTERNSHIP": 6,
                    "SKILLS": 7,
                    "HOBBIES": 4,
                    "INTEREST": 5,
                    "ACHIEVEMENT": 13,
                    "CERTIFICATION": 12,
                    "PROJECT": 19
                }

                text_upper = resume_text.upper()

                for keyword, pts in rules.items():
                    if keyword in text_upper:
                        resume_score += pts
                        st.markdown(f"<p style='color:#1ed760;'>[+] {keyword} found</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='color:black;'>[-] {keyword} missing</p>", unsafe_allow_html=True)

                my_bar = st.progress(0)
                for i in range(resume_score):
                    my_bar.progress(i + 1)
                    time.sleep(0.01)

                st.success(f"Your Resume Score: {resume_score}")

                
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = cur_date + "_" + cur_time

                insert_data(
                    sec_token, ip_add, host_name, dev_user, os_name_ver,
                    str(latlong), city, state, country,
                    act_name, act_mail, act_mob,
                    resume_data["name"], resume_data["email"],
                    str(resume_score), timestamp,
                    str(resume_data["no_of_pages"]), reco_field, cand_level,
                    str(resume_skills), str(recommended_skills),
                    str(rec_course), pdf_file.name
                )

                # --------------------------------------
                # BONUS VIDEOS
                # --------------------------------------
                st.header("Resume Tips 💡")
                st.video(random.choice(resume_videos))

                st.header("Interview Tips 💡")
                st.video(random.choice(interview_videos))

                st.balloons()
    
    elif choice == "Feedback":

       
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = cur_date + "_" + cur_time

        st.subheader("Feedback Form")

        with st.form("feedback_form"):
            feed_name = st.text_input("Name")
            feed_email = st.text_input("Email")
            feed_score = st.slider("Rate Us (1-5)", 1, 5)
            comments = st.text_input("Comments")
            submitted = st.form_submit_button("Submit")

            if submitted:
                insertf_data(feed_name, feed_email, feed_score, comments, timestamp)
                st.success("Thanks for your feedback!")
                st.balloons()

    
        st.subheader("User Ratings Overview")
        query = "SELECT * FROM user_feedback"
        feedback_df = pd.read_sql(query, connection)

        if len(feedback_df) > 0:
            labels = feedback_df.feed_score.unique()
            values = feedback_df.feed_score.value_counts()

            fig = px.pie(values=values, names=labels, title="User Rating Distribution")
            st.plotly_chart(fig)

            st.subheader("User Comments")
            cdf = pd.DataFrame(feedback_df[['feed_name', 'comments']])
            st.dataframe(cdf)


  
    elif choice == "About":
        st.subheader("About The Tool - AI Resume Analyzer")

        st.markdown("""
        <p align='justify'>
        This tool analyzes resumes using Natural Language Processing (NLP).  
        It extracts skills, predicts your field, recommends courses, evaluates resume strength,  
        and helps you improve your chances of getting a job.
        </p>

        <p align='justify'>
        <b>User:</b> Upload your resume and get instant recommendations.  
        <br/><b>Feedback:</b> Tell us how we can improve.  
        <br/><b>Admin:</b> Dashboard for analytics (username: admin, password: admin@resume-analyzer)
        </p>
        """, unsafe_allow_html=True)


   
    else:
        st.subheader("Admin Panel")

        ad_user = st.text_input("Username")
        ad_pass = st.text_input("Password", type="password")

        if st.button("Login"):

            if ad_user == "admin" and ad_pass == "admin@resume-analyzer":

                st.success("Login Successful")

                st.header("User Data Overview")

                cursor.execute("""
                SELECT ID, ip_add, resume_score,
                CONVERT(Predicted_Field USING utf8),
                CONVERT(User_level USING utf8),
                city, state, country
                FROM user_data
                """)

                plot_data = pd.DataFrame(
                    cursor.fetchall(),
                    columns=["ID", "IP", "Resume Score", "Field", "Level", "City", "State", "Country"]
                )

                st.dataframe(plot_data)

                st.subheader("Download User Report")
                st.markdown(get_csv_download_link(plot_data, "User_Data.csv", "Download CSV"), unsafe_allow_html=True)

                # Pie Charts
                st.subheader("Resume Score Distribution")
                fig = px.pie(values=plot_data["Resume Score"].value_counts(),
                             names=plot_data["Resume Score"].unique(),
                             title="Resume Scores")
                st.plotly_chart(fig)

                st.subheader("Predicted Field Distribution")
                fig = px.pie(values=plot_data["Field"].value_counts(),
                             names=plot_data["Field"].unique(),
                             title="Predicted Fields")
                st.plotly_chart(fig)

                st.subheader("User Experience Level Distribution")
                fig = px.pie(values=plot_data["Level"].value_counts(),
                             names=plot_data["Level"].unique(),
                             title="Experience Levels")
                st.plotly_chart(fig)

                st.subheader("User Location Distribution (City)")
                fig = px.pie(values=plot_data["City"].value_counts(),
                             names=plot_data["City"].unique(),
                             title="City Distribution")
                st.plotly_chart(fig)

            else:
                st.error("Invalid Admin Credentials")


def insert_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong,
                city, state, country, act_name, act_mail, act_mob,
                name, email, resume_score, timestamp, page_no,
                predicted_field, user_level, actual_skills,
                recommended_skills, recommended_courses, pdf_name):

    try:
        cursor.execute("""
            INSERT INTO user_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong,
                                  city, state, country, act_name, act_mail, act_mob, Name,
                                  Email_ID, resume_score, Timestamp, Page_no, Predicted_Field,
                                  User_level, Actual_skills, Recommended_skills, Recommended_courses, pdf_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (sec_token, ip_add, host_name, dev_user, os_name_ver, str(latlong), city, state, country,
              act_name, act_mail, act_mob, name, email, resume_score, timestamp, page_no,
              predicted_field, user_level, actual_skills, recommended_skills, recommended_courses, pdf_name))

        connection.commit()

    except Exception as e:
        st.error(f"Database Insert Error: {e}")

def insertf_data(feed_name, feed_email, feed_score, comments, timestamp):
    try:
        cursor.execute("""
            INSERT INTO user_feedback(feed_name, feed_email, feed_score, comments, Timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (feed_name, feed_email, feed_score, comments, timestamp))

        connection.commit()

    except Exception as e:
        st.error(f"Feedback Insert Error: {e}")


run()
