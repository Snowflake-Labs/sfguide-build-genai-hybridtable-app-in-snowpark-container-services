import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
from app_helper import get_snowflake_session, generate_image, add_navigation
from streamlit_drawable_canvas import st_canvas
from snowflake.snowpark.functions import col as _col

# Streamlit config
st.set_page_config(page_title="Tel Co", layout="wide", page_icon="📞")

add_navigation()

if "inpainted_image" not in st.session_state:
    st.session_state.inpainted_image = None


def reset_image():
    st.session_state.inpainted_image = None


@st.cache_data
def get_images() -> pd.DataFrame:
    session = get_snowflake_session()
    images = (
        session.table("IMAGES")
        .order_by(_col("ID"))
        .to_pandas()[
            [
                "CITY_NAME",
                "IMAGE_BYTES",
            ]
        ]
    )
    return images


# Don't cache, to show how metadata can be updated in real time
@st.experimental_fragment(run_every=15)
def get_image_metadata(city_name: str) -> dict:
    session = get_snowflake_session()
    metadata = (
        session.table("IMAGES")
        .filter(_col("CITY_NAME") == city_name)
        .to_pandas()
        .iloc[0]
        .to_dict()
    )
    return {k: v for k, v in metadata.items() if k not in ["IMAGE_BYTES", "FILE_NAME", "LAT", "LON"]}


@st.cache_data
def get_image(city_name: str) -> Image.Image:
    images = get_images()
    image_bytes = images.loc[images["CITY_NAME"] == city_name]["IMAGE_BYTES"].values[0]
    image = Image.open(BytesIO(bytes.fromhex(image_bytes))).convert("RGB")

    return image

st.subheader(":phone: Gen AI Inpainting: Snowpark Container Services")

with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")
with left:
    with st.container(border=True, height=770):
        images = get_images()
        city_name = st.selectbox(
            "Select Image",
            images["CITY_NAME"].unique(),
            on_change=reset_image,
        )
        if city_name:
            base_image = get_image(city_name)

            _, col, _ = st.columns([1, 10, 1])
            with col:
                inpainted_image = st_canvas(
                    background_image=base_image,
                    display_toolbar=False,
                    stroke_color="white",
                    stroke_width=85,
                    width=600,
                )
            data = get_image_metadata(city_name)
            _, col, _ = st.columns([1, 8, 1])
            col.dataframe(
                pd.DataFrame(data, index=[0]), hide_index=True, use_container_width=True
            )
            prompt = st.text_input(
                "Enter prompt", "Cell phone tower, high resolution, where marked"
            )
            generate_image_btn = st.button(
                "Generate Image", type="primary", use_container_width=True
            )
        else:
            # No image selected, which should never happen
            st.stop()

with right:
    if generate_image_btn:
        with st.spinner("Generating image..."):
            generate_image(base_image, inpainted_image, prompt)
    if st.session_state.inpainted_image:
        with st.container(border=True, height=770):
            _, col, _ = st.columns([1, 11, 1])
            with col:
                st.write("#### Generated Image")
                st.image(st.session_state.inpainted_image, use_column_width=True)
