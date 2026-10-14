# MRI Diagnosis System

A Flask-based web application that integrates deep learning-based MRI image classification with patient management workflows.

## Overview

This project explores how a trained deep learning model can be integrated into a web application to support MRI image analysis. It provides a doctor-facing interface for managing patient records, uploading MRI images, viewing model predictions, and handling email-related workflows.

**This is an academic project and is not intended for clinical diagnosis or medical decision-making.**

## Features

- **User authentication:** Doctor registration and login.
- **Patient management:** Maintain patient records through the web interface.
- **MRI image analysis:** Upload an image and obtain a prediction from a trained Keras model.
- **Result interface:** View the prediction returned by the model.
- **Email functionality:** Support diagnosis-related email workflows and account recovery.
- **Database integration:** Store user and patient records using Flask-SQLAlchemy and SQLite.

## Technology Stack

- Python
- Flask
- TensorFlow / Keras
- Flask-SQLAlchemy and SQLite
- Flask-Login
- Flask-WTF / WTForms
- Flask-Mail
- HTML, CSS, JavaScript, and Bootstrap

## Model File

The trained model is not included in this repository because it exceeds GitHub's standard file-size limit.

To run the application, obtain the model file separately and place it at:

`models/MSStrokeModelBestt.h5`

The model must be compatible with the application's existing preprocessing and inference code.

## Configuration

The application uses environment variables for its secret key and email credentials.

Create a local `.env` file using `.env.example` as a reference. Replace the placeholder values with your own configuration. Never commit your `.env` file or email credentials.

## Running Locally

Local setup instructions and the exact dependency versions will be added after verifying the project's dependency list and model requirements.

## Limitations

- Predictions depend on the trained model and the data on which it was developed.
- The application has not been established as a clinically validated diagnostic tool.
- The trained model must be obtained separately to run MRI predictions.

## Future Improvements

- Add automated tests for authentication, patient management, and prediction workflows.
- Improve input validation and error handling for uploaded images.
- Add structured logging and monitoring.
- Improve configuration management and deployment practices.
- Evaluate model performance on representative, independent datasets.
- Strengthen privacy controls and security before any real patient data could be used.
