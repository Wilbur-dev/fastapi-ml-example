# FastAPI App to serve machine learning models

An example of how to use FastAPI to serve machine learning models. This dockerized app serves prediction from a simple Linear Regression model trained over dummy data created in scikit-learn.

## Requirements
Docker and docker-compose installed on your machine. 


## start the app

From the root directory, run
```bash
$ docker-compose up
```  


Go to [http://localhost:8000/docs](http://localhost:8000/docs)

### API Endpoints

Each API presents the following endpoints.
#### `GET /health`
Simple GET request to check that the app is running.

Response body:
```json
{
  "is_alive": true
}
```

#### `POST /predict`

for each sample, predicts the most likely class and returns its probability.

Request body:

```json
{
  "feature1": 0.50,
  "feature2": 0.98
}
```

Response body:

```json
{
  "label": 1,
  "probability": [
    0.02087666131346566,
    0.9791233386865343
  ]
}
```

Also, with curl
```bash
curl -X POST "http://0.0.0.0:8000/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"feature1\":0.5,\"feature2\":0.98}"
```

   

