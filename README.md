# AI-Based Cyber Threat Detection System Using Machine Learning

## Objective
This project implements a comprehensive, full-stack Cyber Threat Detection System. It utilizes multiple machine learning models to detect various forms of cyber threats including network intrusions, system anomalies, phishing pages, and malwares.

## Architecture & Modules
This system is structured into a clean, client-server architecture:

1. **Frontend Dashboard (React 18 / Vite)**: A dynamic user interface for monitoring alerts, analyzing threats, and viewing statistics.
2. **Backend API (FastAPI)**: The core server handling data processing, model inference, and communication with the frontend.
3. **Machine Learning Modules**:
   - **Network Intrusion Detection**: Analyzes network traffic to identify malicious activities.
   - **Log Anomaly Detection**: Parses system logs to find irregular patterns and anomalies.
   - **Email Spam & Phishing Detection**: Evaluates URLs and email payloads to detect phishing attempts.
   - **Malware Analysis**: Inspects executable features and byte structures for malware classification.

## Folder Structure Overview
The project is organized into the following main directories:

- `/backend/`: Contains the FastAPI server, API routes (`/routers`), ML models (`/ml`), data processing scripts, and training scripts.
- `/frontend/`: Contains the React-based frontend dashboard UI components and assets.
- `/docs/`: Contains project documentation and the final academic report (`/docs/reports/`).
- `/backend/data/`: Contains **sample datasets** used for demonstration and model evaluation. *(Note: Datasets have been truncated to a small sample size for submission. Refer to data generation scripts to recreate the full datasets if needed).*
- `/backend/saved_models/`: Stores the pre-trained ML models used by the backend.

## Technologies Used
- **Machine Learning**: `scikit-learn`, `PyTorch`, `transformers`, `pandas`, `numpy`
- **Backend**: `FastAPI`, `SQLAlchemy`, `PostgreSQL`, Python 3.11+
- **Frontend**: `React 18`, `Vite`, `TailwindCSS`, `Recharts`

## Steps to Run the Project

### 1. Backend Setup
1. Ensure Python 3.11+ is installed.
2. Ensure PostgreSQL is running (or use the provided `docker-compose.yml` if applicable).
3. Open a terminal in the project root.
4. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```
5. Run the backend server using the provided root script:
   ```bash
   python run.py
   ```
   *The backend API will be available at http://127.0.0.1:8000*

### 2. Frontend Setup
1. Ensure Node.js (18+) is installed.
2. Open a **new** terminal in the project root.
3. Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will be accessible via the local URL provided in the terminal (usually http://localhost:5173).*
