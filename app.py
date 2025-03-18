import os
import json
import base64
import tempfile
import io
from datetime import datetime
from pathlib import Path

import PyPDF2
import cohere
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Professional ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Cohere client
COHERE_API_KEY = "tAuXCmn54TkMmj0R7z2ViRjmVXvkfutRWFGpuqCJ"
co = cohere.Client(COHERE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

# Function to analyze resume against job description using Cohere
def analyze_resume(resume_text, job_description):
    try:
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer. Analyze the following resume against the job description.
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Provide a detailed analysis including:
        1. Overall match percentage
        2. Strengths of the candidate
        3. Areas for improvement
        4. Missing key skills or keywords
        5. Recommendations for improvement
        
        Format your response as JSON with the following structure:
        {{
            "match_percentage": <percentage as integer>,
            "strengths": [<list of strengths>],
            "areas_for_improvement": [<list of areas for improvement>],
            "missing_keywords": [<list of missing keywords>],
            "recommendations": [<list of recommendations>],
            "summary": "<brief summary paragraph>"
        }}
        """
        
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=2000,
            temperature=0.2,
            stop_sequences=[],
            return_likelihoods="NONE"
        )
        
        # Parse the JSON response
        result_text = response.generations[0].text
        # Extract JSON part
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        json_str = result_text[json_start:json_end]
        
        # Parse JSON
        result = json.loads(json_str)
        return result
    
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")
        return None

# Function to extract important keywords from job description
def extract_keywords(job_description):
    try:
        prompt = f"""
        You are an expert in job requirements analysis. Extract the most important skills, qualifications, and keywords from the following job description.
        
        Job Description:
        {job_description}
        
        Provide your response as a JSON object with the following structure:
        {{
            "technical_skills": [<list of technical skills>],
            "soft_skills": [<list of soft skills>],
            "qualifications": [<list of qualifications>],
            "experience": [<list of experience requirements>],
            "other_keywords": [<list of other important keywords>]
        }}
        """
        
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2,
            stop_sequences=[],
            return_likelihoods="NONE"
        )
        
        # Parse the JSON response
        result_text = response.generations[0].text
        # Extract JSON part
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        json_str = result_text[json_start:json_end]
        
        # Parse JSON
        result = json.loads(json_str)
        return result
    
    except Exception as e:
        st.error(f"Error extracting keywords: {e}")
        return None

# Function to generate PDF report
def generate_pdf_report(analysis_result, resume_text, job_description):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "ATS Resume Analysis Report", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        
        # Add match percentage
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Match Percentage: {analysis_result['match_percentage']}%", 0, 1)
        
        # Add summary
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Summary:", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, analysis_result['summary'])
        
        # Add strengths
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Strengths:", 0, 1)
        pdf.set_font("Arial", "", 12)
        for strength in analysis_result['strengths']:
            pdf.cell(0, 10, f"- {strength}", 0, 1)
        
        # Add areas for improvement
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Areas for Improvement:", 0, 1)
        pdf.set_font("Arial", "", 12)
        for area in analysis_result['areas_for_improvement']:
            pdf.cell(0, 10, f"- {area}", 0, 1)
        
        # Add missing keywords
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Missing Keywords:", 0, 1)
        pdf.set_font("Arial", "", 12)
        for keyword in analysis_result['missing_keywords']:
            pdf.cell(0, 10, f"- {keyword}", 0, 1)
        
        # Add recommendations
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Recommendations:", 0, 1)
        pdf.set_font("Arial", "", 12)
        for recommendation in analysis_result['recommendations']:
            pdf.cell(0, 10, f"- {recommendation}", 0, 1)
        
        # Save PDF to a bytes buffer
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None

# Main function
def main():
    # Add custom CSS
    st.markdown("""
    <style>
    /* Dark Sleek Theme */
    .main {
        background-color: #121212; /* Deep Dark Background */
        color: #e0e0e0; /* Light Text for Contrast */
    }

    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        background: #1e1e1e; /* Slightly Lighter Dark for Depth */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }

    .css-1d391kg {
        padding-top: 3rem;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4a90e2, #1e3a8a); /* Sleek Gradient */
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #1e3a8a, #4a90e2);
        transform: scale(1.05);
    }

    .card {
        background-color: #222; /* Darker Card */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        transition: all 0.3s ease-in-out;
    }

    .card:hover {
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        transform: translateY(-4px);
    }
</style>

    """, unsafe_allow_html=True)
    
    # App title and description
    st.title("📊 Professional ATS Resume Analyzer")
    
    st.markdown("""
    <div class='card'>
    <h3>Transform Your Job Application Process with Advanced AI Analysis</h3>
    <p>Upload your resume and job description to get detailed insights on your application's strengths, 
    missing keywords, and recommendations for improvement.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📄 Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            # Save the file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            
            # Display success message
            st.success(f"Resume uploaded successfully: {uploaded_file.name}")
            
            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                st.session_state['resume_text'] = resume_text
                st.session_state['resume_filename'] = uploaded_file.name
            else:
                st.error("Failed to extract text from the uploaded PDF.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔍 Job Description")
        job_description = st.text_area("Paste the job description here", height=250)
        
        if job_description:
            st.session_state['job_description'] = job_description
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Analysis options
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚙️ Analysis Options")
    
    analysis_col1, analysis_col2, analysis_col3 = st.columns([1, 1, 1])
    
    with analysis_col1:
        if st.button("🔍 Tell Me About the Resume"):
            if 'resume_text' in st.session_state and 'job_description' in st.session_state:
                with st.spinner("Analyzing resume..."):
                    analysis_result = analyze_resume(st.session_state['resume_text'], st.session_state['job_description'])
                    if analysis_result:
                        st.session_state['analysis_result'] = analysis_result
                        st.session_state['show_analysis'] = True
            else:
                st.warning("Please upload a resume and provide a job description first.")
    
    with analysis_col2:
        if st.button("📝 Get Keywords"):
            if 'job_description' in st.session_state:
                with st.spinner("Extracting keywords..."):
                    keywords = extract_keywords(st.session_state['job_description'])
                    if keywords:
                        st.session_state['keywords'] = keywords
                        st.session_state['show_keywords'] = True
            else:
                st.warning("Please provide a job description first.")
    
    with analysis_col3:
        if st.button("📊 Percentage Match"):
            if 'resume_text' in st.session_state and 'job_description' in st.session_state:
                with st.spinner("Calculating match percentage..."):
                    analysis_result = analyze_resume(st.session_state['resume_text'], st.session_state['job_description'])
                    if analysis_result:
                        st.session_state['analysis_result'] = analysis_result
                        st.session_state['show_match'] = True
            else:
                st.warning("Please upload a resume and provide a job description first.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display analysis results
    if 'show_analysis' in st.session_state and st.session_state['show_analysis']:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📋 Resume Analysis Results")
        
        analysis_result = st.session_state['analysis_result']
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Strengths", "Improvements", "Keywords", "Recommendations"])
        
        with tab1:
            st.markdown(f"### Match Percentage: {analysis_result['match_percentage']}%")
            st.markdown(f"**Summary:** {analysis_result['summary']}")
            
            # Visualize match percentage with a gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = analysis_result['match_percentage'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Match Percentage"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "firebrick"},
                        {'range': [50, 75], 'color': "gold"},
                        {'range': [75, 100], 'color': "forestgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 85
                    }
                }
            ))
            
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### Key Strengths")
            for strength in analysis_result['strengths']:
                st.markdown(f"✅ {strength}")
        
        with tab3:
            st.markdown("### Areas for Improvement")
            for area in analysis_result['areas_for_improvement']:
                st.markdown(f"🔄 {area}")
        
        with tab4:
            st.markdown("### Missing Keywords")
            missing_keywords = analysis_result['missing_keywords']
            
            # Create a word cloud-like visualization
            if missing_keywords:
                fig = px.treemap(
                    names=missing_keywords,
                    title="Missing Keywords",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No important keywords are missing. Great job!")
        
        with tab5:
            st.markdown("### Recommendations")
            for recommendation in analysis_result['recommendations']:
                st.markdown(f"💡 {recommendation}")
        
        # Generate PDF report
        if st.button("📥 Download PDF Report"):
            with st.spinner("Generating PDF report..."):
                pdf_buffer = generate_pdf_report(
                    analysis_result,
                    st.session_state['resume_text'],
                    st.session_state['job_description']
                )
                
                if pdf_buffer:
                    b64 = base64.b64encode(pdf_buffer.read()).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="ATS_Analysis_Report.pdf">Click here to download your report</a>'
                    st.markdown(href, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display keywords analysis
    if 'show_keywords' in st.session_state and st.session_state['show_keywords']:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔑 Key Job Requirements")
        
        keywords = st.session_state['keywords']
        
        # Create tabs for different keyword categories
        kt1, kt2, kt3, kt4, kt5 = st.tabs(["Technical Skills", "Soft Skills", "Qualifications", "Experience", "Other Keywords"])
        
        with kt1:
            if keywords['technical_skills']:
                fig = px.bar(
                    x=keywords['technical_skills'],
                    y=[len(skill) for skill in keywords['technical_skills']],
                    labels={'x': 'Skills', 'y': 'Importance'},
                    title="Technical Skills Required",
                    color_discrete_sequence=['#4287f5']
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                for skill in keywords['technical_skills']:
                    st.markdown(f"💻 {skill}")
            else:
                st.info("No specific technical skills were identified.")
        
        with kt2:
            if keywords['soft_skills']:
                for skill in keywords['soft_skills']:
                    st.markdown(f"🤝 {skill}")
            else:
                st.info("No specific soft skills were identified.")
        
        with kt3:
            if keywords['qualifications']:
                for qual in keywords['qualifications']:
                    st.markdown(f"🎓 {qual}")
            else:
                st.info("No specific qualifications were identified.")
        
        with kt4:
            if keywords['experience']:
                for exp in keywords['experience']:
                    st.markdown(f"⏱️ {exp}")
            else:
                st.info("No specific experience requirements were identified.")
        
        with kt5:
            if keywords['other_keywords']:
                for kw in keywords['other_keywords']:
                    st.markdown(f"🔍 {kw}")
            else:
                st.info("No other significant keywords were identified.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display match percentage visualization
    if 'show_match' in st.session_state and st.session_state['show_match']:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📊 Match Analysis")
        
        analysis_result = st.session_state['analysis_result']
        
        # Create a 3D visualization
        match_percentage = analysis_result['match_percentage']
        strengths_count = len(analysis_result['strengths'])
        missing_count = len(analysis_result['missing_keywords'])
        
        # Create data for 3D scatter plot
        df = pd.DataFrame({
            'Category': ['Match Percentage', 'Strengths', 'Missing Keywords'],
            'Value': [match_percentage, strengths_count, missing_count],
            'Size': [match_percentage, strengths_count*10, missing_count*10],
            'Color': ['#4287f5', '#42f54e', '#f54242']
        })
        
        fig = px.scatter_3d(
            df, x='Category', y='Value', z='Size',
            color='Category', size='Size', opacity=0.7,
            color_discrete_sequence=['#4287f5', '#42f54e', '#f54242'],
            title="3D Application Match Analysis"
        )
        
        fig.update_layout(
            scene = dict(
                xaxis_title='Category',
                yaxis_title='Value',
                zaxis_title='Size'
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display missing keywords
        st.subheader("Missing Keywords")
        missing_cols = st.columns(3)
        for i, keyword in enumerate(analysis_result['missing_keywords']):
            with missing_cols[i % 3]:
                st.markdown(f"⚠️ **{keyword}**")
                
        # Add final thoughts
        st.markdown(f"### Final Thoughts")
        st.markdown(analysis_result['summary'])
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd;'>
        <p>Professional ATS Resume Analyzer | Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()