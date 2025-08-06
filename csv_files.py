import os
import tempfile
import pandas as pd
import streamlit as st
from google import genai
from typing import List, Dict


if "model" not in st.session_state:
    st.session_state.model = None

@st.cache_resource
def get_client(api_k):
    return genai.Client(api_key=api_k)

# Configure the page
st.set_page_config(
    page_title="Multi-CSV Analysis with Gemini",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Multi-CSV Relationship Analyzer")
st.markdown("""
Upload multiple CSV files to analyze their concurrent relationships using Google's Gemini 1.5 Flash 8B model.
The AI will identify patterns, correlations, and insights across your datasets.
""")

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google GenAI API Key", type="password")
    if api_key:
        st.session_state.model = get_client(api_key)
        st.success("API key configured!")
    
    st.markdown("""
    **How to use:**
    1. Enter your Google GenAI API key
    2. Upload one or more CSV files
    3. Click 'Analyze Relationships'
    4. View the AI-generated analysis
    """)

# File upload section
uploaded_files = st.file_uploader(
    "Upload CSV files",
    type=["csv"],
    accept_multiple_files=True,
    help="Upload multiple CSV files to analyze their relationships"
)

# Function to process CSV files and extract metadata
def process_files(uploaded_files: List) -> Dict:
    """Process uploaded CSV files and return a dictionary with file info and samples."""
    files_data = {}
    
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Store file information
            files_data[f"file_{idx}"] = {
                "name": uploaded_file.name,
                "size": uploaded_file.size,
                "columns": list(df.columns),
                "sample": df.head(3).to_dict(orient='records'),
                "shape": df.shape,
                "description": f"""
                File Name: {uploaded_file.name}
                Size: {uploaded_file.size} bytes
                Shape: {df.shape} (rows x columns)
                Columns: {list(df.columns)}
                Sample Data:
                {df.head(3).to_markdown(index=False)}
                """
            }
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    return files_data

# Function to generate analysis prompt
def generate_analysis_prompt(files_data: Dict) -> str:
    """Generate a comprehensive prompt for Gemini to analyze CSV relationships."""
    files_info = "\n\n".join([file["description"] for file in files_data.values()])
    
    prompt = f"""
    You are an expert data analyst with deep knowledge of finding relationships between datasets.
    Below are {len(files_data)} CSV files with their metadata and sample data:
    
    {files_info}
    
    Analyze these datasets thoroughly and provide a detailed report covering:
    
    1. **Dataset Overview**:
       - Summary of each dataset's purpose based on column names and sample data
       - Data types and potential measurement units for numeric columns
       - Any immediate observations about data quality or completeness
    
    2. **Cross-Dataset Relationships**:
       - Potential join keys or matching columns between datasets
       - How these datasets might relate to each other in a business/analytical context
       - Any temporal, categorical, or hierarchical relationships
    
    3. **Statistical Insights**:
       - Potential correlations between numeric columns across datasets
       - Notable patterns or trends visible in the sample data
       - Any apparent outliers or anomalies
    
    4. **Business/Research Implications**:
       - How combining these datasets could provide valuable insights
       - Potential analytical questions these datasets could answer together
       - Recommendations for further analysis
    
    5. **Data Integration Suggestions**:
       - Recommended methods for combining these datasets
       - Any data cleaning or transformation needed before integration
       - Potential challenges in merging these datasets
    
    Provide your analysis in clear, well-structured markdown format with appropriate headings.
    Be thorough and specific, referencing actual column names and sample values where relevant.
    """
    
    return prompt

# Main analysis function
def analyze_with_gemini(prompt: str) -> str:
    """Send the analysis prompt to Gemini and return the response."""
    try:
        
        response = st.session_state.model.models.generate_content(model='gemini-1.5-flash-8b-latest', contents=[prompt])
        return response.text
    except Exception as e:
        st.error(f"Error analyzing with Gemini: {str(e)}")
        return None

# Display file information and run analysis
if uploaded_files and api_key:
    with st.spinner("Processing uploaded files..."):
        files_data = process_files(uploaded_files)
    
    # Show file summaries in expanders
    for file_id, file_info in files_data.items():
        with st.expander(f"📄 {file_info['name']} - {file_info['shape'][0]} rows × {file_info['shape'][1]} columns"):
            st.write(f"**Columns:** {', '.join(file_info['columns'])}")
            st.dataframe(pd.DataFrame(file_info['sample']), hide_index=True)
    
    # Analysis button
    if st.button("🔍 Analyze Relationships", use_container_width=True):
        with st.spinner("Generating comprehensive analysis with Gemini 1.5 Flash 8B..."):
            analysis_prompt = generate_analysis_prompt(files_data)
            analysis_result = analyze_with_gemini(analysis_prompt)
        
        if analysis_result:
            st.success("Analysis Complete!")
            st.markdown("## 📝 Cross-Dataset Analysis Report")
            st.markdown(analysis_result)
            
            # Option to download the report
            report_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
            with open(report_file.name, "w") as f:
                f.write(analysis_result)
            
            with open(report_file.name, "r") as f:
                st.download_button(
                    label="Download Analysis Report",
                    data=f,
                    file_name="cross_dataset_analysis.md",
                    mime="text/markdown"
                )
            
            os.unlink(report_file.name)
elif uploaded_files and not api_key:
    st.warning("Please enter your Google GenAI API key in the sidebar to proceed with analysis.")