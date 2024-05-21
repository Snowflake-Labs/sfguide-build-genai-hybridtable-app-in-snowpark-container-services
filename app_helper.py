import os
from typing import Any

import streamlit as st
import torch
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
from snowflake.snowpark.session import Session

def get_credentials() -> dict[str, Any]:
    # Environment variables below will be automatically populated by Snowflake
    try:
        login_token = get_login_token()
        return {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "host": os.getenv("SNOWFLAKE_HOST"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "authenticator": "oauth",
            "token": login_token,
        }
    except (KeyError, FileNotFoundError):
        return st.secrets["connections"]["snowflake"]


def get_login_token():
    with open("/snowflake/session/token", "r") as f:
        return f.read()


def get_connection_params():
    return get_credentials()


def get_snowflake_session() -> Session:
    if "snowflake_session" not in st.session_state:
        session = Session.builder.configs(get_connection_params()).create()
        st.session_state.snowflake_session = session
    return st.session_state.snowflake_session


def generate_image_from_model(
    prompt: str, base_image: Image.Image, inpainted_image: Image.Image
) -> None:
    pipe = get_inpainting_model()
    pipe = pipe.to("cuda")
    image = pipe(prompt=prompt, image=base_image, mask_image=inpainted_image).images[0]
    image.save("inpaint_image.png")

    st.session_state.inpainted_image = "inpaint_image.png"

    st.rerun()


def generate_image(base_image: Image.Image, inpainted_image: Any, prompt: str):
    inpainted_image_data = inpainted_image.image_data[:, :, -1] > 0
    inpainted_image = Image.fromarray(inpainted_image_data)

    try:
        generate_image_from_model(prompt, base_image, inpainted_image)
    except AssertionError:
        image = base_image
        st.session_state.inpainted_image = image


def get_inpainting_model():
    return StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting",
        revision="fp16",
        torch_dtype=torch.float32,
    )


def add_navigation():
    st.sidebar.page_link("app_main.py", label="Gen AI Inpainting", icon="🎨")
    st.sidebar.page_link(
        "pages/unistore_hybrid_tables.py", label="Tower Uptime", icon="🏓"
    )
