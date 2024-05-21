import streamlit as st
from streamlit_folium import st_folium
import folium
from snowflake.snowpark.functions import col
from app_helper import get_snowflake_session, add_navigation

st.set_page_config(page_title="Tower Uptime: Hybrid Tables", page_icon="🏓", layout="wide")

st.subheader(":phone: Tower Uptime: Hybrid Tables")

add_navigation()

def update_table():
    edited_rows = st.session_state["tower_status"]["edited_rows"]
    for id, val in edited_rows.items():
        id = int(id) + 1
        st.toast(f"Updating status for Tower {id} to {val['STATUS']}", icon="✅")
        status = val["STATUS"]
        update_sql = f"update cell_towers_ca set status = '{status}', status_message = '{status}' where tower_id = {id}"
        session.sql(update_sql).collect()

if "bounds" not in st.session_state:
    st.session_state["bounds"] = None

map_display_col, data_display_col = st.columns(2, gap="medium")
with data_display_col:
    with st.container(border=True, height=870):
        status_options = ["Online", "Offline", "Warning"]
        config = {
            "STATUS": st.column_config.SelectboxColumn(
                "Status", options=status_options, required=True
            )
        }
        session = get_snowflake_session()
        data = (
            session.table("cell_towers_ca")
            .order_by(col("TOWER_ID"))
            .limit(50)
            .to_pandas()
        )
        if (
            st.session_state["bounds"] is not None
            and st.session_state["bounds"]["_southWest"]["lat"] is not None
        ):
            data = data[
                (data["LAT"] > st.session_state["bounds"]["_southWest"]["lat"])
                & (data["LAT"] < st.session_state["bounds"]["_northEast"]["lat"])
                & (data["LON"] > st.session_state["bounds"]["_southWest"]["lng"])
                & (data["LON"] < st.session_state["bounds"]["_northEast"]["lng"])
            ]

        st.write("")

        df = st.data_editor(
            data[
                [
                    "TOWER_NAME",
                    "STATUS",
                    "LAT",
                    "LON",
                ]
            ],
            column_config=config,
            disabled=[
                "TOWER_NAME",
                "LAT",
                "LON",
            ],
            use_container_width=True,
            height=800,
            key="tower_status",
            hide_index=True,
            on_change=update_table,
        )

with map_display_col:
    with st.container(border=True, height=870):
        m = folium.Map(location=[37.6313, -122.1201], zoom_start=10)
        fg = folium.FeatureGroup(name="Tower Status")
        # Add markers for each tower
        for index, row in df.iterrows():
            popup_text = f"<b>{row['TOWER_NAME']}</b><br>Status: {row['STATUS']}"
            fg.add_child(
                folium.Marker(
                    location=[row["LAT"], row["LON"]],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"{row['TOWER_NAME']} | Status: {row['STATUS']}",
                    icon=folium.Icon(
                        color="darkred"
                        if row["STATUS"] == "Offline"
                        else "orange"
                        if row["STATUS"] == "Warning"
                        else "darkblue"
                    ),
                )
            )

        st.write("")
        # Render map
        st_data = st_folium(
            m,
            feature_group_to_add=fg,
            width=725,
            height=650,
            returned_objects=["last_object_clicked_tooltip"],
            key="map",
        )

        tooltip = st_data["last_object_clicked_tooltip"]

        if tooltip is not None:
            st.write("**Last selected tower:**")
            tower_name = tooltip.split("|")[0].strip()
            st.dataframe(
                data[data["TOWER_NAME"] == tower_name],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("Click on a tower to see more details", icon="🖱️")
