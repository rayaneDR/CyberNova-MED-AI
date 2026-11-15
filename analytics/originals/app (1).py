from flask import Flask
import random
from analysis import analyze

app = Flask(__name__)
baseline = {"heart_rate": 72, "spo2": 98, "temperature": 36.6}

@app.route("/")
def home():
    data = {
        "heart_rate": random.randint(65, 130),
        "spo2": random.randint(88, 99),
        "temperature": round(random.uniform(36.0, 38.5), 1)
    }
    result = analyze(data, baseline)
    
    color = "green" if result['status'] == 'normal' else "red"
    text = "BIKHIR ✅" if result['status'] == 'normal' else "KHATAR ⚠️"

    return f"""
    <html><body style="text-align:center; font-family:Arial; padding-top:100px">
    <h1>Dashboard dyal Ali</h1>
    <h1 style="color:{color}; font-size:80px">{text}</h1>
    <h2>Qelb: {data['heart_rate']} | SpO2: {data['spo2']} | Temp: {data['temperature']}</h2>
    <h3>{result['alert']}</h3>
    <p>Dir Refresh bach tchof 9iyass jdid</p>
    <button onclick="location.reload()" style="font-size:30px; padding:15px">Refresh</button>
    </body></html>
    """

if __name__ == "__main__":
    app.run(debug=True)