# ARES – AI Strike Risk Predictor

##  Overview

ARES (AI Strike Risk Predictor) is a web application developed during a hackathon, designed to estimate geographical risk levels using artificial intelligence.
The system analyzes historical data and generates predictions that are visualized through an interactive interface.

---

##  How It Works

ARES processes historical datasets using a machine learning model to predict risk levels for specific locations.
The results are served through an API and displayed on an interactive map in the frontend.

---

##  Project Structure

The project is split into two main components:

* **Backend**

  * Python server
  * Machine learning model
  * Data processing scripts

* **Frontend**

  * User interface
  * Interactive risk map visualization

---

## Tech Stack

### Backend

* Python
* FastAPI
* Scikit-learn
* Pandas

### Frontend

* React
* Vite
* JavaScript
* CSS

---

##  Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Suciu869/ares.git
cd ares
```

---

### 2. Run the Backend

```bash
cd backend

# create virtual environment
python -m venv venv

# activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# start server
uvicorn main:app --reload
```

---

### 3. Run the Frontend

```bash
cd frontend

# install dependencies
npm install

# start development server
npm run dev
```

After starting both services, open the local link provided by Vite in your browser.

---

##  Contribution & Role

During the hackathon, my main responsibilities included:

* Designing and training the machine learning model
* Implementing the backend using FastAPI
* Building the API for predictions
* Collaborating on integration between backend and frontend

---

##  Purpose

This project demonstrates how AI can be used to:

* Analyze historical data
* Predict risk patterns
* Deliver results through a modern web interface

---

