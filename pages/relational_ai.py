import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from app_helper import add_navigation, get_snowflake_session, read_html_file
from streamlit_folium import st_folium

st.set_page_config(page_title="Graph Analysis: Snowflake Native Apps", page_icon="🤖", layout="wide")

st.subheader(":phone: Graph Analysis: Snowflake Native Apps")

add_navigation()

session = get_snowflake_session()


@st.cache_data
def get_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = session.table("TOWER_CLUSTERS").to_pandas()
    edges_df = session.table("TOWER_EDGES").to_pandas()
    node_to_coordinates = dict(
        zip(data["TOWER_ID"].astype(int), zip(data["LAT"], data["LON"]))
    )
    edges_df["SOURCE_LOCATION"] = edges_df["SOURCE_ID"].map(node_to_coordinates)
    edges_df["TARGET_LOCATION"] = edges_df["TARGET_ID"].map(node_to_coordinates)
    locations = edges_df[
        ["SOURCE_ID", "TARGET_ID", "SOURCE_LOCATION", "TARGET_LOCATION", "DISTANCE"]
    ].values.tolist()
    return data, locations


data, locations = get_data()

map_display_col, data_display_col = st.columns(2, gap="medium")
with map_display_col:
    with st.container(border=True, height=710):
        # Get locations between edges
        node_to_coordinates = dict(
            zip(data["TOWER_ID"].astype(int), zip(data["LAT"], data["LON"]))
        )

        # Set map center and zoom level
        m = folium.Map(location=[37.6313, -122.1201], zoom_start=10, control_scale=True)

        # Add markers and offline markers to the map
        for _, row in data.iterrows():
            status = "Status: " + row["STATUS"]
            popup_content = "Tower: " + str(row["TOWER_ID"]) + "<br>" + status
            iframe = folium.IFrame(popup_content)
            popup = folium.Popup(iframe, min_width=200, max_width=200)
            folium.Marker(
                location=[row["LAT"], row["LON"]],
                popup=popup,
                tooltip=popup_content,
                icon=folium.Icon(color=row["COLOR"], icon="tower-cell", prefix="fa"),
                c=row["TOWER_ID"],
            ).add_to(m)

            # Add black circle markers for offline towers
            if row["STATUS"] != "Online":
                offline_marker = folium.CircleMarker(
                    location=[row["LAT"], row["LON"]],
                    color="black",
                    weight=1,
                    fill_opacity=0.6,
                    opacity=1,
                    fill_color="black",
                    fill=False,
                )
                offline_marker.add_to(m)

        # Add polylines between coordinates
        for src_id, tgt_id, point1, point2, distance in locations:
            src_status = data.loc[data["TOWER_ID"] == src_id, "STATUS"].iloc[0]
            tgt_status = data.loc[data["TOWER_ID"] == tgt_id, "STATUS"].iloc[0]

            dash_value = (
                10 if (src_status != "Online") or (tgt_status != "Online") else 0
            )

            folium.PolyLine(
                locations=[point1, point2],
                color="#494848",
                tooltip="{:.2f}".format(distance),
                weight=4,
                dash_array=dash_value,
            ).add_to(m)

        # Display the folium map in Streamlit
        st_folium(m, width=725, height=650)

with data_display_col:
    with st.container(border=True, height=710):
        st.dataframe(data, use_container_width=True, height=650)


@st.cache_data
def show_graph() -> None:
    html_content = read_html_file("graph.html")
    components.html(html_content, height=1000)


show_graph()
