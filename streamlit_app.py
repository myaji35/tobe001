import pandas as pd
import streamlit as st
from openpyxl import load_workbook

st.set_page_config(
    layout="wide",
    page_icon="🤣"
)

# Title and description
st.title("AI NLG Process and System")
st.markdown("_Tobe's : Natural Language Generation v0.4.1_")

# Function to load data with error handling (considering potential CSV and XLSX files)
def load_data(file):
    try:
        # Attempt to read as CSV first (common for sales data)
        data = pd.read_csv(file, header=0)
        return data
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        try:
            # If CSV fails, attempt to read as XLSX using openpyxl
            wb = load_workbook(file, read_only=True)
            ws = wb.active
            data = pd.DataFrame(ws.values)
            
            # Set the first row as the column names
            data.columns = data.iloc[0]
            data = data[1:]
            
            return data
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None

def Domestic_Foreign_sum(df):
    try:
        df["내외국인수"] = df["내국인계"] + df["외국인계"]
        return df
    except KeyError as e:
        st.error(f"필드를 찾을 수 없습니다.: {str(e)}")
    except Exception as e:
        st.error(f"내외국인수 필드를 추가하는 중 오류가 발생했습니다.: {str(e)}")

def get_domestic_foreign_percentile(df):
    max_value = df["내외국인수"].max()
    min_value = df["내외국인수"].min()

    # Define a function to calculate the '백분위' field
    def calculate_percentile(row):
        return 100 * (row - min_value) / (max_value - min_value) 

    # Add the '백분위' field to the dataframe and calculate it
    df["백분위"] = df["내외국인수"].apply(calculate_percentile)
    return df

# Create two columns for Streamlit sidebar and work area
col1, col2 = st.columns([1, 3])

# Streamlit sidebar
with col1:
    expander = st.sidebar.expander("File Upload", expanded=True)
    with expander:
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    
    # Add a horizontal line
    st.sidebar.markdown("---")
    
    # Add a "Next2 Step" button
    if st.sidebar.button("1. 내외국인수 = 내국인계 + 외국인계"):
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            if df is not None:
                df = Domestic_Foreign_sum(df)
                st.session_state.df_domestic_foreign = df.copy()  # Use df.copy() to avoid SettingWithCopyWarning
        else:
            st.warning("파일을 업로드해주세요.")
    # Add a "Next Step" button
    if st.sidebar.button("2. 총세대수 백분위"):
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            if df is not None:
                df = get_domestic_foreign_percentile(df)  # Call the get_domestic_foreign_percentile function
                st.session_state.df_domestic_foreign = df.copy()  # Use df.copy() to avoid SettingWithCopyWarning
        else:
            st.warning("파일을 업로드해주세요.")

# Work area
with col2:
    col2_container = st.container()
    with col2_container:
        
        if uploaded_file is not None:
            # Try loading data using the function
            try:
                df = load_data(uploaded_file)
                if df is not None:
                    # Check if data was loaded successfully
                    tab1, tab2, tab3 = st.tabs(["Uploaded Data", "내외국인수","총세대수 백분위"])
                    
                    with tab1:
                        tab1_container = st.container()
                        with tab1_container:
                            st.subheader(f"Uploaded Data : {uploaded_file.name}")
                        
                            # Apply CSS style to align content after load_data to the left
                            st.markdown(
                                """
                                <style>
                                div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
                                    display: flex;
                                    flex-direction: column;
                                    align-items: flex-start;
                                }
                                </style>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Display the DataFrame
                            st.dataframe(df)
                    
                    with tab2:
                        tab2_container = st.container()
                        with tab2_container:
                            if 'df_domestic_foreign' in st.session_state:
                                st.subheader("내외국인수")
                                st.success("내외국인수 필드가 추가되었습니다.")
                                st.dataframe(st.session_state.df_domestic_foreign)
                            else:
                                st.info("내외국인수를 계산하려면 '1. 가상수치 : 내외국인수 = 내국인 + 외국인' 버튼을 누르세요.")
                    with tab3:
                        tab3_container = st.container()
                        with tab3_container:
                            if 'df_domestic_foreign' in st.session_state:
                                st.subheader("총세대수 백분위")
                                st.success("총세대수 백분위 필드가 추가되었습니다.")
                                st.dataframe(st.session_state.df_domestic_foreign)
                            else:
                                st.info("총세대수 백분위를 계산하려면 '2. 총세대수 백분위' 버튼을 누르세요.")
            except Exception as e:
                # Catch any unexpected errors
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.info("Please upload a file.")