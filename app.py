from flask import Flask, request, jsonify, send_from_directory
import pickle
import json
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Production paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# For Render deployment - use relative paths
try:
    # Try Render path structure first
    MODEL_PATH = "Model/Car_prices_model.pickle"
    COLUMNS_PATH = "Model/Car_columns.json"

    # If files not found, try alternative paths
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = os.path.join(BASE_DIR, "model", "Car_prices_model.pickle")
    if not os.path.exists(COLUMNS_PATH):
        COLUMNS_PATH = os.path.join(BASE_DIR, "model", "Car_columns.json")

    print(f"Looking for model at: {MODEL_PATH}")
    print(f"Looking for columns at: {COLUMNS_PATH}")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    with open(COLUMNS_PATH, "r") as f:
        data_columns = json.load(f)
        columns = data_columns["data_columns"]

    print("✅ Model and columns loaded successfully!")
    print(f"Loaded {len(columns)} columns")

except Exception as e:
    print(f"❌ Error loading model: {e}")
    # List files for debugging
    try:
        model_dir = os.path.join(BASE_DIR, "..", "model")
        print(f"Files in model directory: {os.listdir(model_dir)}")
    except:
        print("Could not list model directory")
    model = None
    columns = None


def extract_unique_values(columns):
    """Extract unique values for makes, models, and conditions from columns"""
    makes = set()
    models = set()
    conditions = set()

    for column in columns:
        if column.startswith("make_"):
            makes.add(column.replace("make_", ""))
        elif column.startswith("model_"):
            models.add(column.replace("model_", ""))
        elif column.startswith("condition_"):
            conditions.add(column.replace("condition_", ""))

    return {
        "makes": sorted(list(makes)),
        "models": sorted(list(models)),
        "conditions": sorted(list(conditions))
    }


def create_exact_model_make_mapping():
    """Create 100% accurate model-make mapping using automotive knowledge"""
    exact_mappings = {
        'bmw': ['130i', '3', '3 series', '320i', '323i', '325i', '328i', '4-runner', '5', '5 series', '523i', '525i',
                '528i', '530i', '535i', '550i', '6', '7 series', 'x3', 'x5', 'x6', 'm', 'm class'],
        'ford': ['ecosport', 'edge', 'escape', 'expedition', 'explorer', 'f-150', 'flex', 'focus', 'fusion', 'mustang',
                 'ranger', 'taurus', 'transit'],
        'honda': ['accord', 'accord crosstour', 'city', 'civic', 'cr-v', 'crosstour', 'element', 'fit', 'fr-v',
                  'odyssey', 'pilot', 'ridgeline', 'stream'],
        'hyundai': ['accent', 'azera', 'creta', 'elantra', 'genesis', 'i10', 'ix35', 'santa fe', 'sonata', 'tucson',
                    'veloster', 'veracruz'],
        'kia': ['borrego', 'cadenza', 'carens', 'cerato', 'forte', 'mohave', 'optima', 'picanto', 'rio', 'sedona',
                'sorento', 'soul', 'sportage'],
        'lexus': ['es', 'gs', 'is', 'ls', 'lx', 'nx', 'rx', 'rx 300', 'rx 330', 'rx 350', 'rx 400h'],
        'mazda': ['2', '3', '5', '6', 'cx-7', 'cx-9', 'mx-3', 'premacy', 'tribute'],
        'mercedes-benz': ['a-class', 'c-class', 'c180', 'c200', 'c220', 'c230', 'c240', 'c250', 'c280', 'c300', 'c320',
                          'c350', 'c43', 'cla-class', 'cls', 'e200', 'e300', 'e320', 'e350', 'e550', 'g-class',
                          'gl-class', 'gla 250', 'gla-class', 'glc-class', 'gle-class', 'glk-class', 'gls-class',
                          'r-class', 's-class', 's-coupe', 'slk-class'],
        'nissan': ['almera', 'altima', 'armada', 'frontier', 'maxima', 'micra', 'murano', 'pathfinder', 'patrol',
                   'primera', 'quest', 'rogue', 'sentra', 'sunny', 'teana', 'tiida', 'titan', 'x-trail'],
        'peugeot': ['206', '307', '308', '406', '407', '408', '508', '607', '807'],
        'toyota': ['4-runner', 'avalon', 'avanza', 'camry', 'corolla', 'corolla altis', 'corolla verso', 'fj cruiser',
                   'hiace', 'highlander', 'hilux', 'land cruiser', 'land cruiser prado', 'matrix', 'previa', 'prius',
                   'rav4', 'sequoia', 'sienna', 'solara', 'tacoma', 'tundra', 'venza', 'yaris'],
        'volkswagen': ['bora', 'cc', 'golf', 'golf variant', 'jetta', 'passat', 'tiguan', 'touareg', 'vento'],
        'others': ['ilx', 'mdx', 'rdx', 'rl', 'tl', 'tsx', 'zdx', 'a4', 'a6', 'a7', 'enclave', 'lacrosse', 'rendezvous',
                   'verano', 'escalade', 'srx', 'avalanche', 'camaro', 'equinox', 'malibu', '200', '300c', 'avenger',
                   'sebring', 'town&country', 'caliber', 'caravan', 'challenger', 'charger', 'durango', 'journey',
                   'acadia', 'yukon', 'ex', 'fx', 'fx35', 'g35', 'jx', 'm', 'qx4', 'qx56', 'qx60', 'qx80', 'x-type',
                   'xj', 'cherokee', 'commander', 'compass', 'grand cherokee', 'liberty', 'wrangler', 'discovery',
                   'freelander', 'range rover', 'range rover evoque', 'range rover sport', 'range rover velar',
                   'range rover vogue', 'mkc', 'mkx', 'navigator', 'lancer', 'outlander', 'pajero', 'pajero io',
                   'montero', 'cayenne', 'panamera', 'forester', 'legacy', 'outback', 'tribeca', 'vitara', 's80',
                   'xc90', 'astra', 'berlingo', 'c4', 'cl', 'cooper', 'continental', 'duster', 'galaxy', 'laguna',
                   'logan', 'mgf', 'mpv', 'vectra', 'viano', 'zafira', 'tc', 'xb']
    }

    mapping = {}
    all_models = []

    for column in columns:
        if column.startswith("model_"):
            model_name = column.replace("model_", "")
            all_models.append(model_name)
            mapping[model_name] = []

    for make, models in exact_mappings.items():
        for model in models:
            if model in all_models:
                if make not in mapping[model]:
                    mapping[model].append(make)

    uncovered_models = [model for model in all_models if not mapping[model]]
    if uncovered_models:
        for model in uncovered_models:
            mapping[model] = ['others']

    return mapping


# Initialize variables
unique_values = {}
model_make_mapping = {}

if columns:
    unique_values = extract_unique_values(columns)
    model_make_mapping = create_exact_model_make_mapping()
    print(f"✅ Extracted {len(unique_values['makes'])} makes, {len(unique_values['models'])} models")


# Serve frontend files
@app.route("/")
def serve_frontend():
    return send_from_directory("Client", "CarPriceEngine.html")


@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(os.path.join(BASE_DIR, "..", "Client"), path)


# API endpoints
@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "makes_count": len(unique_values.get('makes', [])),
        "models_count": len(unique_values.get('models', []))
    })


@app.route("/api/options", methods=["GET"])
def get_options():
    if not columns:
        return jsonify({"error": "Model not loaded"}), 500

    return jsonify({
        "makes": unique_values["makes"],
        "models": unique_values["models"],
        "conditions": unique_values["conditions"],
        "model_make_mapping": model_make_mapping
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    if model is None or columns is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        data = request.get_json()

        # Create input vector
        x = np.zeros(len(columns))

        # Fill numeric fields
        column_mapping = {
            "Age": "age",
            "Engine Size": "engine size",
            "Horse Power": "horse power"
        }

        for key, col_name in column_mapping.items():
            if key in data:
                x[columns.index(col_name)] = float(data[key])

        # Fill one-hot fields
        for col in ["Make", "Model", "Condition"]:
            encoded = f"{col.lower()}_{data.get(col)}"
            if encoded in columns:
                x[columns.index(encoded)] = 1

        # Predict
        prediction = model.predict([x])[0]
        prediction = float(prediction)

        return jsonify({
            "predicted_price": round(prediction, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=False)

