import streamlit as st
import google.generativeai as genai
import json
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini AI Pro response
def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    return response.text

# Function to extract text from PDF resume
def input_pdf_text(upload_file):
    reader = pdf.PdfReader(upload_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey,
Fill the missing keywords with high accuracy.
resume:{text}
description:{jd}

I want to respond in one single string having structure
{{"JD Match": "%", "Missing Keywords": [], "Profile Summary": ""}}
"""

# Streamlit app
st.title("***Welcome To ATS***")
st.subheader("***Applicant Tracking System***")
st.text("Let's, Improve your Resume ATS")
jd = st.text_area("Paste Your dream job Description")
upload_file = st.file_uploader("Upload Your Resume", type="Pdf", help="Please Upload Your Resume")

submit = st.button("Submit")

# Function to analyze resume text and get response
def analyze_resume(upload_file, jd):
    text = input_pdf_text(upload_file)
    if text:
        with st.spinner("Analyzing Your Resume..."):  # Display spinner while processing
            response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            return response
    else:
        st.error("Error: Unable to extract text from the uploaded file.")

# Main function
if submit:
    if upload_file is not None:
        response = analyze_resume(upload_file, jd)
        st.markdown(response)
        if response:
            try:
                parsed_data = json.loads(response)
                jd_match = parsed_data.get("JD Match")
                missing_keywords = parsed_data.get("Missing Keywords")
                profile_summary = parsed_data.get("Profile Summary")
                if jd_match is not None and missing_keywords is not None and profile_summary is not None:
                    st.subheader("Job Description Match")
                    st.markdown(f'<div style="background-color: green; padding: 3px; border-radius: 5px;">'
                                    f'<center style="color: white;">{jd_match}</center>'
                                    f'</div>', unsafe_allow_html=True)
                    st.subheader("Missing Keywords")
                    for keyword in missing_keywords:
                        st.markdown(f'<font color="red">{keyword}</font>', unsafe_allow_html=True)
                    st.subheader("Profile Summary")
                    st.write(profile_summary)
            except json.JSONDecodeError:
                st.error("Error: Unable to parse the response.Please give one more slap on submit button")
        else:
            st.error("Error: No response received.Please give one more slap on submit button")
    else:
        st.error("Error: No file uploaded.")
