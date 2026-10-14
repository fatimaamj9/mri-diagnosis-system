# MRI Diagnosis System

A web application built with Flask that integrates a deep learning model for experimental MRI image classification.

## Overview

This project explores the integration of a trained deep learning model into a web application designed for doctors. Users can register and log in, manage patient records, upload MRI images, and view model-generated classification results.

The application also includes email-related functionality for diagnosis communications and account recovery.

**Disclaimer:** This is an academic project, not a clinically validated diagnostic system. Its predictions must not be used as a substitute for professional medical assessment.

## Features

- Doctor registration and login
- Patient record management
- MRI image upload and model inference
- Display of classification results
- Email-related functionality
- Password recovery
- Database integration for user and patient records

## Technology Stack

- **Backend:** Python, Flask
- **Deep learning:** TensorFlow, Keras
- **Database:** Flask-SQLAlchemy, SQLite
- **Authentication:** Flask-Login
- **Forms and validation:** Flask-WTF, WTForms
- **Email:** Flask-Mail
- **Frontend:** HTML, CSS, JavaScript, Bootstrap

## Model Information

The saved model is stored separately from this repository because of its large file size.

The application expects the model at:

`models/MSStrokeModelBestt.h5`

The saved model accepts RGB images with input dimensions of 300 × 300 pixels and returns a single sigmoid output. The exact class mapping and preprocessing requirements have not yet been independently verified.

## Privacy and Data

Do not commit real patient images, identifiable medical information, credentials, or private configuration files to this repository.

Any images used for demonstration should be authorized for reuse and de-identified. Model predictions are experimental and should not be interpreted as confirmed medical diagnoses.

## Running Locally

### Prerequisites

- Python
- Git
- The trained model file, obtained separately

### 1. Clone the repository

```bash
git clone https://github.com/fatimaamj9/mri-diagnosis-system.git
cd mri-diagnosis-system
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the values with your own configuration. Never commit secret keys, email passwords, or other credentials to GitHub.

### 5. Add the trained model

Obtain the trained model separately and place it at:

`models/MSStrokeModelBestt.h5`

The model file is not included in this repository because of its large size.

### 6. Start the application

For local development, run:

```bash
python app.py
```

For a deployment environment using Gunicorn, the configured command is:

```bash
gunicorn app:app
```


## Future Improvements

- Add automated tests for authentication, patient management, and prediction workflows.
- Improve uploaded-image validation and error handling.
- Verify and document the model's preprocessing and class mapping.
- Improve configuration management and secret handling.
- Add structured logging and monitoring.
- Improve the user interface and accessibility.
- Evaluate model performance using appropriate independent datasets.

## License

No license has been specified yet. Please contact the project owner before reusing or redistributing this project.
