def analyze(measurement, baseline):
    # baseline = les valeurs normales dyal raed
    # measurement = la mesure jdida

    user_id = measurement.get("user_id") or measurement.get("astronaut_id") or "unknown"

    heart_rate = measurement.get("heart_rate") or measurement.get("hr") or 0
    spo2 = measurement.get("spo2") or 0
    temperature = measurement.get("temperature") or measurement.get("temp") or 0

    # 1. Sensor failure : ila capteur khaser
    if heart_rate == 0 or spo2 == 0:
        return {
            "user_id": user_id,
            "status": "sensor_failure",
            "alert": "sensor khaser - check capteur"
        }

    # 2. Anomaly : ila 9elb tale3 bzaf wla habet bzaf
    if heart_rate > 120 or heart_rate < 40 or spo2 < 90 or temperature > 38.5:
        return {
            "user_id": user_id,
            "status": "anomaly",
            "alert": "khatar - heart_rate / spo2 machi normal"
        }

    # 3. Normal
    return {
        "user_id": user_id,
        "status": "normal",
        "alert": None
    }