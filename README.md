# AI-Resume-Analyzer
# AI-Resume-Analyzer

A Python-based tool that analyzes resumes using Natural Language Processing (NLP) to extract key information, evaluate skills, and provide insights/recommendations.

---

## 🔍 Features

- Parse resumes (PDF, DOCX) to extract structured information (education, experience, skills)  
- Keyword-based clustering of resumes into job sectors or domains  
- Resume scoring or rating based on predefined metrics  
- Provide suggestions or feedback (e.g., missing skills, improvements)  
- Analytics / visualizations for resume data (optional / if implemented)  

---

## 📦 Tech Stack

- **Language**: Python  
- **Libraries**: (example) `spaCy`, `pyresparser`, `pdfminer` (or whatever you're using)  
- **Data processing**: NLP, parsing  
- **Visualization**: (if any) `matplotlib`, `seaborn`, or dashboard library  

---

## 🚀 Getting Started

### 1. Clone the repository  
```bash
git clone https://github.com/savitar007-droid/AI-Resume-Analyzer.git  
cd AI-Resume-Analyzer  

### 2. Create virtual environment
Windows:
python -m venv venv
venv\Scripts\activate

Linux / Mac:
python3 -m venv venv
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Download NLP model (if using spaCy)
python -m spacy download en_core_web_sm

▶️ Running the Project
Run using command:
python src/analyzer.py --file resumes/sample.pdf

Or use inside Python:
from src.analyzer import ResumeAnalyzer
analyzer = ResumeAnalyzer("resumes/sample.pdf")
result = analyzer.parse()
print(result["skills"])
print(result["education"])


Processed output is stored inside:

/output 
