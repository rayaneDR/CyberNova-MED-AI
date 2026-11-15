from analysis import analyze

baseline = {}

# 1. Normal
print("Test 1:")
print(analyze({"user_id": "ali_01", "heart_rate": 74, "spo2": 98, "temperature": 36.6}, baseline))

# 2. Anomaly
print("Test 2:")
print(analyze({"user_id": "ali_01", "heart_rate": 180, "spo2": 88, "temperature": 39.0}, baseline))

# 3. Sensor failure
print("Test 3:")
print(analyze({"user_id": "ali_01", "heart_rate": 0, "spo2": 0, "temperature": 0}, baseline))