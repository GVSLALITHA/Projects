import streamlit as st
import datetime
import pandas as pd
from joblib import load
import matplotlib.pyplot as plt

# Load the trained model
model = load("RandomForestRegressor_model.joblib")

def main():
    html_temp = """
    <div style = "background-color:#6a1b9a;padding:16px">
    <h2 style="color:black;text-align:center;">Car Dekho Price Prediction</h2>
    </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)
    st.write('')
    st.write('')
    st.markdown("Let's sell your car at the best price!")

    # Input fields
    p1 = st.number_input("What is the current ex-showroom price of the car (in Lakhs)", 1.5, 85.0, step=1.0)
    p2 = st.number_input("What is the total distance covered (in Kilometers)", step=100)
    
    s1 = st.selectbox("What is the fuel type of the car", ('Diesel', 'Petrol', 'Lpg', 'Cng', 'Electric'))
    if s1 == 'Cng':
        p3 = 0
    elif s1 == 'Diesel':
        p3 = 1
    elif s1 == 'Electric':
        p3 = 2
    else:
        p3 = 4
    
    s2 = st.selectbox("What is the transmission type?", ('Manual', 'Automatic'))
    p4 = 1 if s2 == "Manual" else 0

    p5 = st.slider("Number of owners the car previously had", 0, 4)

    date_time = datetime.datetime.now()
    year = st.number_input("Year of purchase", 1990, date_time.year)
    p6 = date_time.year - year

    # Create DataFrame for model prediction
    data_new = pd.DataFrame({
        'Price': [p1],
        'Distance_Travelled': [p2],
        'Fuel_Type': [p3],
        'Transmission': [p4],
        'Owner': [p5],
        'Year_of_purchase': [p6]
    })

    # Prediction button
    if st.button('Predict'):
        predicted_price = model.predict(data_new)
        st.success(f'You can sell your car at {predicted_price[0]:.2f} Lakhs')
# Run the app
if __name__ == "__main__":
    main()
