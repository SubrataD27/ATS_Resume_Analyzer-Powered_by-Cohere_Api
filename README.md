# Professional ATS Resume Analyzer

## Overview
The **Professional ATS Resume Analyzer** is a Streamlit-based web application that leverages AI (Cohere API) to evaluate resumes against job descriptions, providing insights into match percentage, strengths, areas for improvement, missing keywords, and recommendations.

## Features
- Extracts text from uploaded PDF resumes.
- Analyzes resume content against job descriptions.
- Provides ATS-friendly insights, including:
  - Match percentage
  - Strengths and weaknesses
  - Missing key skills
  - Recommendations for improvement
- Extracts important keywords from job descriptions.
- Generates a detailed analysis report in PDF format.
- Interactive UI with data visualizations using Plotly.

## Tech Stack
- **Backend:** Cohere API for AI-based analysis
- **Frontend:** Streamlit for UI
- **Libraries:**
  - `PyPDF2` for PDF text extraction
  - `cohere` for AI-based text processing
  - `streamlit` for web interface
  - `pandas`, `matplotlib`, `plotly` for data processing and visualization
  - `FPDF` for PDF report generation
  - `PIL` for image processing

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ats-resume-analyzer.git
   cd ats-resume-analyzer
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
2. Upload a resume in PDF format.
3. Provide the job description.
4. Click the **Analyze Resume** button to generate insights.
5. Download the ATS analysis report in PDF format.

## Environment Variables
Create a `.env` file and add your Cohere API key:
```
COHERE_API_KEY=your_api_key_here
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author
**Subrata Dhibar**


