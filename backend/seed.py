import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE_NAME", "landsafe")]

zones = [
    {
        "id": "SKM-04",
        "name": "North Sikkim · Zone 04",
        "state": "Sikkim",
        "lat": 27.53,
        "lon": 88.52,
        "slope": 78,
        "historicalRisk": 82,
        "rainfall": 89,
        "sevenDayRainfall": 74,
        "soilMoisture": 81,
        "groundMovement": 62,
        "population": 3240,
        "level": "critical"
    },
    {
        "id": "SKM-01",
        "name": "East Sikkim · Zone 01",
        "state": "Sikkim",
        "lat": 27.31,
        "lon": 88.61,
        "slope": 69,
        "historicalRisk": 73,
        "rainfall": 62,
        "sevenDayRainfall": 68,
        "soilMoisture": 71,
        "groundMovement": 38,
        "population": 1840,
        "level": "high"
    },
    {
        "id": "ASM-02",
        "name": "Dima Hasao · Zone 02",
        "state": "Assam",
        "lat": 25.50,
        "lon": 93.02,
        "slope": 64,
        "historicalRisk": 66,
        "rainfall": 56,
        "sevenDayRainfall": 51,
        "soilMoisture": 64,
        "groundMovement": 35,
        "population": 2180,
        "level": "high"
    }
]

alerts = [
    {
        "zone": "North Sikkim · Zone 04",
        "detail": "Critical risk · NH-310A road exposure",
        "time": "12 min ago",
        "level": "critical"
    },
    {
        "zone": "East Sikkim · Zone 01",
        "detail": "Heavy rainfall · field check recommended",
        "time": "34 min ago",
        "level": "high"
    }
]

sensors = [
    {"id": "SKM-04", "status": "online"},
    {"id": "SKM-05", "status": "online"},
    {"id": "ASM-02", "status": "online"},
    {"id": "MEG-02", "status": "offline"}
]

db.zones.delete_many({})
db.alerts.delete_many({})
db.sensors.delete_many({})

db.zones.insert_many(zones)
db.alerts.insert_many(alerts)
db.sensors.insert_many(sensors)

print("Seed data inserted successfully.")