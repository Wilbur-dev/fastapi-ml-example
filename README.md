# FastAPI App to serve machine learning models

An example of how to use FastAPI to serve machine learning models.

## Requirements

Python 3.6+

## Installation
Install the required packages in your local environment.
```bash
pip install -r requirements
``` 

### creating the model

This app serves a simple Linear Regression model trained over dummy data created in scikit-learn. The model is serialized using joblib. To generate the serialized model, run
```bash
$ cd app/sklearn_model
$ python ml_train.py
```
This will generate the model and save in `/app/sklearn_model`

## start the app

1. Start the application from the root dir:  
```bash
 uvicorn app.main:app --reload
```

2. Go to [http://localhost:8000/docs](http://localhost:8000/docs)

### API Endpoints

Each API presents the following endpoints.
#### `GET /health`
Simple GET request to check that the app is running.

Response body:
```json
{
  "is_alive": True
}
```

#### `POST /predict`

for each sample, predicts the most likely class and returns its probability.

Request body:

```json
{
  "feature1": 0.1,
  "feature2": 0.5
}
```

Response body:

```json
{
  "label": 0,
  "probability": [
    0.9998993774602198,
    0.00010062253978017755
  ]
}
```

Also, with curl
```bash
curl -X POST "http://127.0.0.1:8000/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"feature1\":0.1,\"feature2\":0.5}"
```

   

