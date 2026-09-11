import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import requests

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.txt")
load_dotenv(BASE_DIR / "atlas-credentials.env")

app = Flask(__name__)
CORS(app)

mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
if not mongo_uri:
    raise RuntimeError("Missing MONGO_URI or MONGODB_URI in backend environment files")

mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = mongo[os.getenv("DATABASE_NAME", "landsafe")]


def risk_level(score):
    if score <= 30:
        return "low"
    if score <= 50:
        return "moderate"
    if score <= 70:
        return "high"
    return "critical"


def calculate_risk(zone):
    factors = {
        "rainfall": zone.get("rainfall", 0) * 0.30,
        "sevenDayRainfall": zone.get("sevenDayRainfall", 0) * 0.20,
        "slope": zone.get("slope", 0) * 0.15,
        "historicalRisk": zone.get("historicalRisk", 0) * 0.15,
        "soilMoisture": zone.get("soilMoisture", 0) * 0.10,
        "groundMovement": zone.get("groundMovement", 0) * 0.10,
    }

    score = round(sum(factors.values()))

    return {
        "score": score,
        "level": risk_level(score),
        "factors": {
            key: round(value)
            for key, value in factors.items()
        },
    }


@app.get("/api/zones")
def get_zones():
    zones = list(db.zones.find({}, {"_id": 0}))
    return jsonify(zones)


@app.get("/api/zones/<zone_id>")
def get_zone(zone_id):
    zone = db.zones.find_one({"id": zone_id}, {"_id": 0})

    if not zone:
        return jsonify({"error": "Zone not found"}), 404

    return jsonify(zone)


@app.post("/api/risk")
def calculate_zone_risk():
    zone = request.get_json()
    result = calculate_risk(zone)

    return jsonify({
        "zone": zone.get("name"),
        **result
    })


@app.get("/api/alerts")
def get_alerts():
    alerts = list(db.alerts.find({}, {"_id": 0}))
    return jsonify(alerts)


@app.get("/api/reports")
def get_reports():
    reports = list(db.reports.find({}, {"_id": 0}))
    return jsonify(reports)


@app.post("/api/reports")
def create_report():
    report = request.get_json()

    report["status"] = "unverified"
    report["submittedAt"] = datetime.utcnow().isoformat()

    db.reports.insert_one(report)
    report.pop("_id", None)

    return jsonify(report), 201


@app.get("/api/sensors")
def get_sensors():
    total = db.sensors.count_documents({})
    online = db.sensors.count_documents({"status": "online"})

    return jsonify({
        "total": total,
        "online": online,
        "offline": total - online
    })


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "LANDSAFE-NER API"
    })


@app.get("/api/weather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    url = "https://api.openweathermap.org/data/2.5/weather"

    response = requests.get(url, params={
        "lat": lat,
        "lon": lon,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metric"
    })

    return jsonify(response.json())


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)
