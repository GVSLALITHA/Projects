import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image

# Define fish class labels
fish_classes = [
    "animal fish",
    "animal fish bass",
    "fish sea_food black_sea_sprat",
    "fish sea_food gilt_head_bream",
    "fish sea_food hourse_mackerel",
    "fish sea_food red_mullet",
    "fish sea_food red_sea_bream",
    "fish sea_food sea_bass",
    "fish sea_food shrimp",
    "fish sea_food striped_red_mullet",
    "fish sea_food trout"
]

# Load the VGG16 model
@st.cache_resource
def load_vgg16_model():
    model = load_model("/content/tl_model_v1.weights.best.h5")  # Ensure model is in the correct path
    return model

model = load_vgg16_model()

# Image preprocessing function
def preprocess_input_image(img):
    img = img.convert("RGB")  # Ensure image has 3 channels (RGB)
    img = img.resize((128, 128))  # Resize to match model input size
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Streamlit UI
st.title("Fish Classification")
st.write("Upload an image to classify the fish species using the VGG16 model.")

# Upload Image
uploaded_file = st.file_uploader("📂 Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 Uploaded Image", use_column_width=True)

    # Preprocess the image
    img_array = preprocess_input_image(image)

    # Make predictions
    predictions = model.predict(img_array)

    # Get the class with the highest probability
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_label = fish_classes[predicted_class_index]
    confidence_score = predictions[0][predicted_class_index] * 100  # Convert to percentage

    # Display the predicted fish species
    st.write(f"###Predicted Fish Species: **{predicted_label}**")
    st.write(f"**Confidence Score:** {confidence_score:.2f}%")

    # Show confidence scores for all classes
    st.subheader("Prediction Confidence for All Classes:")
    for fish, prob in zip(fish_classes, predictions[0]):
        st.write(f"{fish}: **{prob * 100:.2f}%**")  # Confidence in percentage
