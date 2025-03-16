from flask import Flask, jsonify
import json

app = Flask(__name__)

# Load JSON data
def load_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        return {"error": str(e)}

# Endpoint 1: Serve individual stock data
@app.route("/stocks", methods=["GET"])
def get_stocks():
    data = load_json("stock_data.json")
    return jsonify(data)

# Endpoint 2: Serve sector data
@app.route("/sectors", methods=["GET"]) 
def get_sectors():
    data = load_json("sector_data.json")
    return jsonify(data)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)