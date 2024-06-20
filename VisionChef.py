import streamlit as st
from functions import *
import requests
from backend.api.restegourmet import *
import shutil
from PIL import Image

# Function to set the background image
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/pastel-yellow-soft-gradient-blur-background_53876-105434.jpg");
            background-attachment: fixed;
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
add_bg_from_url()  # Apply background image

# Title and logo section
col1, col2 = st.columns([1, 5])
with col1:
    image = Image.open("logo.png")
    st.image(image, use_column_width=True) # Display logo
with col2:
    st.markdown("# VisionChef") # Display title

# Introduction section
st.markdown("""
### Take a snap, cook like a pro!
##### 📷 1. Take a picture of your leftover ingredients
##### 📜 2. Get recipes for gourmet meals
""")

# File uploader
uploaded_file = st.file_uploader("Upload an image ", type=["jpg", "jpeg", "png"])

# Function to save uploaded file to temporary location
def save_to_temp_file(uploaded_file):
    with open("temp_file_from_user.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

# Function to copy image to the root folder
def save_image_to_root(image_path):
    new_image_path = "temp_file_from_user.jpg"
    shutil.copy2(image_path, new_image_path)

# Example images
example_images = [
    'sample_images/Apple-Puree-3-Ways-2.jpg',
    'sample_images/carbropotonionbean.jpg',
    'sample_images/tomeggon.jpg'
]

# Selection of uploaded or example images
with st.expander("or select one from our examples"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(example_images[0], width=200)
    with col2:
        st.image(example_images[1], width=200)
    with col3:
        st.image(example_images[2], width=200)
    option = st.radio(
        "",
        ("My uploaded image", "Example 1", "Example 2", "Example 3"),
        index=0
    )

# Determine image to use
image_url = None
if option == "My uploaded image" and uploaded_file is not None:
    image_url = "temp_file_from_user.jpg"
elif option == "Example 1":
    image_url = example_images[0]
    save_image_to_root(image_url)
elif option == "Example 2":
    image_url = example_images[1]
    save_image_to_root(image_url)
elif option == "Example 3":
    image_url = example_images[2]
    save_image_to_root(image_url)

# Functions to interact with APIs and display results
def show_URL(codes):
    en_ingr = get_values_from_dict(codes, int_EN_dict)
    st.write("We found the following ingredients:", ", ".join(en_ingr))
    de_ingr = EN2DE(en_ingr, EN_DE_dict)
    url_to_visit = generate_restegourmet_url(de_ingr)
    st.write(url_to_visit)

def show_widgets(codes):
    en_ingr = get_values_from_dict(codes, int_EN_dict)
    de_ingr = EN2DE(en_ingr, EN_DE_dict)
    everything = check_image_urls(must_can_funct(",".join(de_ingr))[:6])
    recipes = everything[:6]
    num_columns = 3
    for i in range(0, len(recipes), num_columns):
        columns = st.columns(num_columns)
        for j, recipe in enumerate(recipes[i:i + num_columns]):
            with columns[j]:
                st.image(recipe["image_url"], use_column_width=True)
                st.markdown(f'<a href="{recipe["url"]}" target="_blank">{recipe["name"]}</a>', unsafe_allow_html=True)

def call_api(uploaded_file, is_buffer=False):
    api_url = "https://finalmodel-phec24vmza-ey.a.run.app/predict"
    params = {"image_filename": uploaded_file if is_buffer else uploaded_file.getbuffer()}
    response = requests.post(api_url, files=params)
    return filter_dict_by_value(response.json(), "0.2")

def relabel(codes):
    with st.expander("You can re-label your ingredients"):
        st.image("https://finalmodel-phec24vmza-ey.a.run.app/public/local_img.jpg")
        selected = st.multiselect("", unique_values(int_EN_dict), get_values_from_dict(codes, int_EN_dict))
        return lookup_keys(selected, int_EN_dict)

# Main processing logic
if uploaded_file is not None:
    with open("temp_file_from_user.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    codes = call_api(uploaded_file)
    codes = relabel(codes)
    show_widgets(codes)
elif uploaded_file is None and option != "My uploaded image":
    file_tmp = image_url
    with open(file_tmp, 'rb') as f:
        codes = call_api(f, True)
        codes = relabel(codes)
        show_widgets(codes)
