import requests

data = {
    "Make": "Toyota",
    "Model": "Corolla",
    "Condition": "Foreign Used",
    "Age": 3,
    "Engine Size": 1.8,
    "Horse Power": 140
}

response = requests.post("http://127.0.0.1:5000/predict", json=data)
print(response.json())
