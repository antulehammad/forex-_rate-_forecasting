```markdown
# 💱 Forex Forecasting + Currency Converter

This project is a web application that forecasts foreign exchange (Forex) rates and provides a built-in currency converter.  
It uses **Streamlit** for the interactive interface and **SARIMAX** for time series forecasting.

---

## 🚀 Features

- 📈 **Forecasting:** Predicts future exchange rates using SARIMAX time series model.  
- 💵 **Currency Converter:** Instantly converts values between multiple currencies.  
- 📊 **Interactive Charts:** Visualize trends and predictions with Plotly.  
- 🧠 **Data Preprocessing:** Cleans and transforms daily Forex rate data for model training.  
- 💾 **Modular Design:** Includes separate scripts for data, model, and UI.

---

## 🧩 Technologies Used

- **Python 3.x**
- **Streamlit** – for frontend and dashboard  
- **Pandas** – for data handling  
- **Plotly** – for visualization  
- **Statsmodels (SARIMAX)** – for forecasting  
- **Scikit-learn** – for evaluation metrics  

---

## 📁 Project Structure

```

forex_forecasting_app/
│
├── main.py              # Streamlit app UI
├── model.py             # SARIMAX model training & forecasting
├── utils.py             # Data loading and helper functions
├── daily_forex_rates.csv # Dataset (optional)
├── requirements.txt     # Dependencies
└── README.md            # Project documentation

````

---

## ⚙️ How to Run

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
````

### 2️⃣ Run the Streamlit app

```bash
streamlit run main.py
```

### 3️⃣ Open the browser

Streamlit will show a local URL like:

```
http://localhost:8501
```

---

## 📊 Model Evaluation

The model performance is evaluated using metrics like:

* **MAE (Mean Absolute Error)**
* **MSE (Mean Squared Error)**
* **RMSE (Root Mean Squared Error)**
* **MAPE (Mean Absolute Percentage Error)**

---

## 🔮 Future Enhancements

* Add deep learning models (LSTM, Prophet)
* Deploy on cloud (Streamlit Cloud / AWS)
* Add auto data updates via APIs
* Multi-currency portfolio forecasting

---

## 👨‍💻 Author

**Hammad Antule**
Data Science & AI Enthusiast

---

## 🪪 License

This project is open-source and free to use for learning and research purposes.

```

---

Would you like me to make this README slightly more **stylish with emojis, badges, and better section headers** (still simple but professional-looking for GitHub)?
```
