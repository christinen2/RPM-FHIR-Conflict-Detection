from flask import Flask, jsonify, request
import sys
import math

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "poc"))


from src.api import get_conflicts, count_resources

app = Flask(__name__)


@app.route("/api/detect-conflicts", methods=["POST"])
def detect_conflicts():
    fhir_data = request.json
    report = get_conflicts(fhir_data)
    
    return jsonify({
        "conflicts": make_json_safe(report)
    })

@app.route("/api/count-resources", methods=["POST"])
def count_fhir_resources():
    fhir_data = request.json

    count = count_resources(fhir_data)

    return jsonify(count)


# helper
def make_json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    return value

if __name__ == "__main__":
    print("Starting Server at http://127.0.0.1:5500")
    app.run(debug=True, port=5500)

