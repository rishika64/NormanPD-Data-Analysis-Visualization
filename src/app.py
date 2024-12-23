import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from utils.assignment0 import loadpdf, extract

# App structure
st.set_page_config(layout="wide", page_title="Norman PD Incident Data")
st.title("Incident Data Analysis & Management")
st.sidebar.title("Welcome!")

# Sidebar Navigation
if "page" not in st.session_state:
    st.session_state["page"] = "Home"  

# Sidebar Buttons for Navigation
st.sidebar.header("Navigate to:")
if st.sidebar.button("Home"):
    st.session_state["page"] = "Home"
if st.sidebar.button("Data Exploration"):
    st.session_state["page"] = "Data Exploration"
if st.sidebar.button("Data Visualization"):
    st.session_state["page"] = "Data Visualization"

page = st.session_state["page"]  

# Select date
today = datetime.now()
min_date = today - timedelta(days=30)  # only applicable for past month
max_date = today
if "extracted_data" not in st.session_state:
    st.session_state["extracted_data"] = pd.DataFrame()  




# Home Page
if page == "Home":
    st.header("Norman Police Department, OK")
    st.write("""
    Explore Norman PD incident data, engineer features, and visualize insights 
    to gain deeper understanding and make data-driven decisions.
    """)



# Data Exploration
elif page == "Data Exploration":
    st.header("Extract Incident Data")
    date = st.date_input("Select a Date:", max_value=max_date, min_value=min_date)

    if st.button("Fetch Data"):
        st.write(f"Fetching data for {date}...")

        # Create URL for user selected date
        url = f"https://www.normanok.gov/sites/default/files/documents/{date.strftime('%Y-%m')}/{date.strftime('%Y-%m-%d')}_daily_arrest_summary.pdf"

        # Download and process the PDF
        file_data = loadpdf(url)
        if file_data:
            incidents = extract(file_data)  
            if not incidents.empty:
                st.session_state["extracted_data"] = pd.concat(
                    [st.session_state["extracted_data"], incidents], ignore_index=True
                )
                st.success(f"Extracted {len(incidents)} incidents!")
            else:
                st.warning("No incidents found in the selected date's PDF.")
        else:
            st.error("Failed to fetch or process the PDF for the selected date.")

    # Display Extracted Data
    if not st.session_state["extracted_data"].empty:
        st.subheader("Extracted Incident Data")
        st.dataframe(st.session_state["extracted_data"])
    else:
        st.warning("No data has been extracted yet.")



# Data Visualization
elif page == "Data Visualization":
    if st.session_state["extracted_data"].empty:
        st.warning("No data extracted yet! Go to 'Data Exploration' first.")
    else:
        st.header("Data Visualization")

        data = st.session_state["extracted_data"]  # use extracted data

        # Visualization: Bar Graph
        if "Date" in data.columns and not data["Date"].isnull().all():
            st.subheader("Bar Graph: Dates with Maximum Offenses")
            date_counts = data["Date"].value_counts().reset_index()
            date_counts.columns = ["Date", "Offenses"]
            date_counts = date_counts.sort_values(by="Offenses", ascending=False)

            # Bar Graph
            st.bar_chart(
                date_counts.set_index("Date")["Offenses"],
                use_container_width=True,
            )
        else:
            st.warning("The extracted data does not contain 'Date' information.")


        # Visualization: Clustering 
        if "Time" in data.columns and "Offense" in data.columns:
            st.subheader("Clustering: Offenses in Norman, OK")
            offense_data = (
                data.groupby("Time")
                .size()
                .reset_index(name="Offense Count")
                .sort_values("Time")
            )

            # Plot 
            plt.figure(figsize=(10, 6))
            plt.scatter(offense_data["Time"], offense_data["Offense Count"], alpha=0.7, s=100, c=offense_data["Offense Count"], cmap="viridis")
            plt.title("Clustering: Offenses by Time in Norman, OK")
            plt.xlabel("Time of Day")
            plt.ylabel("Number of Offenses")
            plt.colorbar(label="Offense Count")
            st.pyplot(plt)
            
        else:
            st.warning("The extracted data does not contain sufficient information for clustering.")


        # Visualization: Heatmap
        if "Time" in data.columns and not data["Time"].isnull().all():
            st.subheader("Heatmap: Offense Trend by Time")
            data["Hour"] = data["Time"].str.extract(r"(\d{2})").astype(float)
            hour_counts = data.groupby("Hour").size().reset_index(name="Offenses")
            heatmap_data = hour_counts.set_index("Hour").reindex(range(24), fill_value=0)

            # Plot
            plt.figure(figsize=(12, 2))
            sns.heatmap(
                [heatmap_data["Offenses"]],
                cmap="coolwarm",
                cbar=True,
                xticklabels=heatmap_data.index,
                yticklabels=["Offenses"],
                linewidths=0.1,
            )
            st.pyplot(plt)
        else:
            st.warning("The extracted data does not contain 'Time' information.")
