# Flight Delay Prediction & Deployment System

---

# Executive Summary

This whitepaper presents the design, development, and deployment of an end-to-end machine learning system built to predict average flight departure delays for a major airline. The system transforms raw Bureau of Transportation Statistics flight data into a production-ready REST API capable of serving real-time delay predictions.

The project integrates:

* Structured data ingestion and cleaning
* Feature engineering and polynomial Ridge regression modeling
* MLflow experiment tracking
* Automated MLProject pipeline orchestration
* REST API deployment using FastAPI
* Containerization via Docker
* CI/CD automation using GitLab

The final solution enables business units to submit arrival airport and time parameters through HTTP requests and receive predicted average departure delay (in minutes) in JSON format.

This implementation demonstrates a complete MLOps lifecycle — from raw data to reproducible model deployment in a containerized environment.

---

# 1. Organizational Context

Airline operations depend on accurate delay forecasting for:

* Route planning
* Crew scheduling
* Gate allocation
* Customer communication
* Operational risk mitigation

Leadership requested a deployable system that could:

1. Predict average departure delay from a selected origin airport
2. Be reusable across business units
3. Support automated retraining
4. Integrate with existing software systems

This project fulfills those requirements through a modular and scalable architecture.

---

# 2. System Architecture Overview

The system was developed across four primary layers:

1. Data Engineering Layer
2. Model Development & Experimentation
3. Pipeline Automation
4. Deployment & Productionization

Each layer was version-controlled and documented within GitLab to ensure reproducibility and collaboration.

---

# 3. Data Engineering & Preparation

## 3.1 Data Source

Flight delay data was obtained from the Bureau of Transportation Statistics. The dataset included:

* Scheduled departure time
* Scheduled arrival time
* Destination airport
* Departure delay (minutes)

## 3.2 Data Cleaning Pipeline

Custom Python classes were developed to:

* Load raw CSV data
* Remove null values
* Strip whitespace inconsistencies
* Convert time fields to datetime objects
* Remove extreme outliers (>60 minutes)
* Filter data to a specific origin airport

All transformations were scripted to ensure reproducibility. Cleaned datasets were versioned using date-stamped backups.

## 3.3 Feature Engineering

The modeling dataset was structured as:

* One-hot encoded destination airport
* Scheduled departure time (seconds)
* Scheduled arrival time (seconds)
* Weekday indicator

The target variable was average departure delay (minutes).

---

# 4. Model Development & Experiment Tracking

## 4.1 Modeling Approach

A polynomial Ridge regression model was implemented to capture nonlinear relationships while controlling overfitting through L2 regularization.

Hyperparameter tuning was conducted across multiple alpha values.

## 4.2 Experiment Tracking with MLflow

MLflow experiments were implemented to log:

* Alpha parameter values
* Mean Squared Error (MSE)
* Root Mean Squared Error (average delay deviation)
* Model artifacts

Nested MLflow runs were used to:

* Track each hyperparameter iteration
* Record final optimal model metrics

This ensured full experiment traceability.

## 4.3 Model Selection

Model performance was evaluated using:

* Mean Squared Error (MSE)
* Average delay deviation (√MSE)

The optimal alpha value was selected based on lowest validation MSE.

The final trained model was exported as:

* `finalized_model.pkl`
* `airport_encodings.json`

---

# 5. Pipeline Automation with MLProject

To ensure reproducibility across environments, an MLProject configuration file was created linking:

1. Data ingestion script
2. Data filtering/cleaning script
3. Polynomial regression model script

Parameters were passed via command-line arguments to allow scalable retraining across airports.

This structure enables analysts in other business units to rerun the full training pipeline with minimal modification.

---

# 6. API Development & Production Interface

## 6.1 Framework Selection

FastAPI was selected for its:

* High performance
* Automatic OpenAPI documentation
* Built-in validation
* Ease of integration

## 6.2 Implemented Endpoints

### Root Endpoint

`/`

Returns confirmation that the API is operational.

### Prediction Endpoint

`/predict/delays`

Accepts:

* arrival_airport_id
* departure_time
* arrival_time

Returns:

* JSON response containing predicted average departure delay

### Health Endpoint

`/health`

Returns model diagnostic information for verification and debugging.

## 6.3 Validation & Error Handling

The API includes:

* Input validation
* Proper HTTP error codes
* Handling of invalid airport identifiers
* Handling of incorrectly formatted times

---

# 7. Unit Testing & Quality Assurance

Unit tests were written using pytest to validate:

* Correct endpoint responses
* Proper error handling
* Missing parameter behavior
* Model inference functionality

Testing ensures system reliability prior to container build.

---

# 8. Containerization with Docker

## 8.1 Docker Configuration

A Dockerfile was created to:

* Install dependencies from requirements.txt
* Copy application code and model artifacts
* Expose port 8000
* Launch FastAPI via Uvicorn

## 8.2 Reproducibility Considerations

Dependency versions were pinned (e.g., scikit-learn) to avoid model incompatibility issues.

## 8.3 Docker Compose

A docker-compose configuration was implemented to streamline rebuild and deployment.

---

# 9. CI/CD Integration

GitLab CI/CD automation:

1. Runs unit tests
2. Builds Docker image
3. Pushes image to container registry
4. Deploys container

This ensures consistent deployment and version traceability.

---

# 10. Operational Impact

The deployed system enables:

* Real-time delay estimation
* Cross-department integration
* Consistent retraining
* Scalable experimentation

The architecture separates model training from serving infrastructure, enabling independent iteration.

---

# 11. Strategic Recommendations

1. Expand model features to include weather and congestion indicators.
2. Implement rolling retraining schedule.
3. Monitor production prediction drift.
4. Introduce model performance dashboards.
5. Consider migration to gradient boosting models for improved predictive power.

---

# 12. Conclusion

This project demonstrates the complete lifecycle of a machine learning system — from data ingestion to containerized API deployment.

By combining data engineering, experiment tracking, automation, API design, containerization, and CI/CD integration, the system delivers a reproducible and scalable predictive solution aligned with enterprise standards.

The implementation reflects production-grade MLOps principles and provides a foundation for future expansion across additional airports and operational units.
