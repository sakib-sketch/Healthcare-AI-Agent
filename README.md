# MediCode AI: Agentic Healthcare Coding MVP 🏥🤖

An automated, multi-agent system designed to streamline medical billing by translating clinical notes into ICD-10 codes using advanced AI reasoning.

## 🚀 Overview
MediCode AI utilizes a **4-Agent Workflow** to process doctor's clinical documentation. Instead of a single model, the system uses specialized agents that work together, audit each other, and ensure high accuracy in medical coding.

### 🤖 The Agent Team
1.  **Extractor Agent:** Parses messy clinical notes into structured entities (Diagnoses, Symptoms, Meds).
2.  **Coder Agent:** Maps extracted diagnoses to official **ICD-10-CM** billing codes.
3.  **Auditor Agent:** Validates the codes for accuracy and provides a confidence score.
4.  **Reporting Agent:** Generates a final billing report and exports it to CSV/Excel.

## 🛠️ Tech Stack
*   **Brain:** Cohere Command-R (Agentic LLM)
*   **Framework:** LangChain
*   **UI:** Streamlit (Custom Premium CSS)
*   **Backend:** Python 3.12

## 📦 Installation & Setup

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/Healthcare-AI-Agent.git
    cd Healthcare-AI-Agent
    ```

2.  **Setup Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    COHERE_API_KEY=your_api_key_here
    MODEL_NAME=command-r
    ```

5.  **Run the App:**
    ```bash
    $env:OPENBLAS_NUM_THREADS=1; streamlit run frontend/app.py
    ```

## 👥 Contributors
*   **Sakib Nadaf**
*   **Sagnik**

## 🎓 Mentor
*   **Arindam Ghosh**
