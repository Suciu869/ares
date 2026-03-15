# ares

A.R.E.S. Backend - Advanced Risk Evaluation System
This repository contains the prediction engine and API for the A.R.E.S. tactical defense platform. It uses machine learning to estimate the risk level of missile and drone attacks across different regions of Ukraine.

System Overview
The backend is responsible for three main tasks:

Data Management: Storing and retrieving strategic information about regional infrastructure and front-line proximity.

Machine Learning Inference: Running a HistGradientBoosting model to calculate attack probabilities based on real-time inputs.

API Delivery: Serving these predictions to the React frontend through a high-performance FastAPI server.

Technical Stack
Language: Python 3.10 or higher.

Framework: FastAPI (for RESTful API development).

AI Library: Scikit-Learn (specifically the HistGradientBoostingClassifier ensemble).

Data Processing: Pandas and NumPy.

Server: Uvicorn (ASGI server).

File Descriptions
api.py: The main server file that handles incoming requests and CORS configuration.

model.pkl: The serialized machine learning model bundle including encoders and feature names.

dataset_strategic_id.csv: A database of regional vulnerability scores and geographical data.

antrenareModel.py: The script used to train the model using historical attack datasets.

requirements.txt: A file listing all necessary Python libraries for deployment.
