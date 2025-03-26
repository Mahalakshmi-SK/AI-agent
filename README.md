# Tutor-AI Project

A full-stack application combining a FastAPI backend and a React frontend, aimed at providing a seamless user experience for learning and tutoring.

## Prerequisites
To run this project, ensure you have the following installed on your machine:
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)
- npm (comes with Node.js)

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Ron-Caster/Tutor-AI.git
cd Tutor-AI
```

### 2. Install Dependencies

#### a. Root Folder
In the **root folder**, install the dependency for running both backend and frontend together:
```bash
npm install
```

#### b. Frontend Folder
Navigate to the **frontend** folder and install its dependencies:
```bash
cd frontend
npm install
```

### 3. Run the Application
Return to the root directory and use the following command to start both the backend and frontend simultaneously:
```bash
cd ..
npm run dev
```

- The backend will run on: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- The frontend will run on: [http://localhost:5173](http://localhost:5173)

---

## File Structure
```plaintext
.
├── backend/
│   ├── app.py       # FastAPI application
│   ├── other backend files...
├── frontend/
│   ├── src/         # React frontend source files
│   ├── package.json # Frontend dependencies
├── package.json      # Root package.json
├── README.md         # Project documentation (this file)
```

---

## Troubleshooting
1. If you encounter issues with missing dependencies, ensure you’ve run `npm install` in the correct directories.
2. Backend requires `uvicorn` to be installed. Make sure you’ve installed it with `pip`:
   ```bash
   pip install uvicorn
   ```