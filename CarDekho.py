import streamlit as st
import pandas as pd
import numpy as np
import joblib  # For loading trained model

# Load pre-trained model and scaler
model, feature_names, scaler = joblib.load("car_price_model.pkl")



# Encoding Mappings
bt_encoding = {
    'Hatchback': 10.5, 'Sedan': 12.8, 'SUV': 15.2, 'MUV': 9.4, 'Pickup Trucks': 8.7, 'Minivans': 14.1,
    'Coupe': 16.5, '': 7.0, 'Convertibles': 18.3, 'Wagon': 13.2, 'Hybrids': 20.0
}

oem_encoding = {
    'Hyundai': 11.2, 'Maruti': 8.5, 'Skoda': 13.4, 'BMW': 20.1, 'Tata': 9.3, 'Mahindra': 10.7,
    'Volkswagen': 12.0, 'Honda': 10.9, 'Renault': 9.5, 'Chevrolet': 8.8, 'Audi': 18.2, 'Toyota': 14.5,
    'Jaguar': 22.0, 'Kia': 10.0, 'Ford': 11.5, 'Jeep': 15.6, 'Datsun': 7.8, 'Mitsubishi': 13.0,
    'Mercedes-Benz': 25.0, 'Volvo': 17.4, 'MG': 12.5, 'Land Rover': 21.5, 'Nissan': 9.7, 'Isuzu': 14.0,
    'Porsche': 30.2, 'Fiat': 10.5, 'Mini': 19.8, 'Lexus': 26.4
}

transmission_mapping = {'Manual': 0, 'Automatic': 1}

fuel_types = ['Cng', 'Diesel', 'Electric', 'Lpg', 'Petrol']
cities = ['Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Jaipur', 'Kolkata']

oem_models = {
    'Hyundai': ['i20', 'Grand i10', 'Verna', 'Creta', 'Xcent'],
    'Maruti': ['Swift', 'Celerio', 'Wagon R', 'Swift Dzire', 'Alto 800'],
    'Skoda': ['Superb', 'Kodiaq', 'Slavia', 'Octavia', 'Rapid'],
    'BMW': ['X1', '5 Series', '7 Series', 'X5', '3 Series'],
    'Tata': ['Zest', 'Nexon', 'Harrier', 'Nano', 'Tiago'],
    'Mahindra': ['XUV300', 'XUV500', 'Scorpio', 'Thar', 'Bolero'],
    'Volkswagen': ['Ameo', 'Polo', 'Vento', 'Taigun', 'Virtus'],
    'Honda': ['City', 'Amaze', 'Brio', 'Jazz', 'WR-V']
}

st.title("Car Price Prediction 🚗💰")

# User Inputs
bt = st.selectbox("Select Body Type", list(bt_encoding.keys()))
transmission = st.selectbox("Select Transmission", list(transmission_mapping.keys()))
owner_no = st.number_input("Enter Owner Number (0-5)", min_value=0, max_value=5, step=1)
oem = st.selectbox("Select OEM", list(oem_encoding.keys()))
model_selected = st.selectbox("Select Model", oem_models[oem])
distance = st.number_input("Enter Distance Driven (in KM)", min_value=0)
car_age = st.number_input("Enter Car Age", min_value=2, max_value=40)

selected_fuel = st.selectbox("Select Fuel Type", fuel_types)
selected_city = st.selectbox("Select City", cities)

# Apply Encoding
bt_encoded = bt_encoding[bt]
oem_encoded = oem_encoding[oem]
transmission_encoded = transmission_mapping[transmission]

# Encode Model by Assigning an Index within OEM Category
model_index = oem_models[oem].index(model_selected) / (len(oem_models[oem]) - 1)

# One-Hot Encoding for Fuel Type and City
fuel_encoded = [1 if fuel == selected_fuel else 0 for fuel in fuel_types]
city_encoded = [1 if city == selected_city else 0 for city in cities]

# Separate scaling and non-scaling features
features_to_scale = np.array([[bt_encoded, oem_encoded, model_index, distance, car_age]])
scaled_features = scaler.transform(features_to_scale)[0]  # Flatten to 1D

# Combine scaled and non-scaled features
input_data = np.concatenate(([transmission_encoded, owner_no], scaled_features, fuel_encoded, city_encoded)).reshape(1, -1)

if st.button("Predict Price"):
    predicted_price = model.predict(input_data)
    st.success(f"**Predicted Car Price: {predicted_price[0]:.2f} Lakhs**")
