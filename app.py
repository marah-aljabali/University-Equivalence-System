import streamlit as st
from enter_data import enter_data
from uploade_best_match import uploade_best_match

# Basic page settings
st.set_page_config(
  page_title="Academic Plan Equivalency Tool",
  page_icon="",
  layout="wide"
)

# Main interface
st.title("Academic Plan Equivalency Tool")
st.markdown(
  "Upload the complete study plans for the old and new majors to receive a comprehensive equivalency report "
  "(maximum of 30 equivalent credit hours)."
)


  
# Input method selection
options = ["Upload Files", "Enter Data"]
selected_options = st.selectbox(
  "Choose input method",
  options
)

if "Upload Files" in selected_options:
  uploade_best_match()
if "Enter Data" in selected_options:
  enter_data()