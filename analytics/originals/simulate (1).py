import time
import random
from analysis import analyze

baseline = {"heart_rate": 72, "spo2": 98, "temperature": 36.6}

print("Capteur khedam...")

while True:
    data = {
        "user_id": "ali_01",
        "heart_rate": random.randint(65, 130),
        "spo2": random.randint(88, 99),
        "temperature": round(random.uniform(36.0, 38.5), 1)
    }

    result = analyze(data, baseline)
    print(f"Qelb: {data['heart_rate']} | SpO2: {data['spo2']} | Status: {result['status']} | Alert: {result['alert']}")
    
    time.sleep(2)