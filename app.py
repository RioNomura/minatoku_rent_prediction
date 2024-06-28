from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# モデルを読み込む
model = joblib.load('rent_prediction_model.joblib')

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    if request.method == 'POST':
        area = float(request.form['area'])
        access = float(request.form['access'])
        age = float(request.form['age'])
        
        # 予測
        input_data = pd.DataFrame([[age, area, access]], columns=['築年数', '面積', 'アクセス'])
        prediction = model.predict(input_data)[0]
        prediction = round(prediction, 2)
    
    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
