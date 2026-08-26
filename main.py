# Imports
from pathlib import Path
from PIL import Image, ImageOps
import json
import os
import pandas as pd
import requests
import streamlit as st

# Gets the directory of the currently running script and sets the current ticket image path
project_dir = os.path.dirname(os.path.abspath(__file__))
ticket_image_path = f'{project_dir}/data/ticket.jpeg'

# Texas Lotto CSV URL and project file paths
url = "https://www.texaslottery.com/export/sites/lottery/Games/Lotto_Texas/Winning_Numbers/lottotexas.csv"
csv_file = f'{project_dir}/data/texas-lotto.csv'
user_file = f'{project_dir}/numbers.json'

# Gets the winning numbers for the selected drawing date, displays them and then highlights them in the user's numbers dataframe
def get_winning_numbers():
    for index, row in st.session_state['csv_df'].iterrows():
        if row["Draw Date"] == st.session_state['selected_date']:
            st.session_state['winning_numbers'] = row.iloc[1:7].tolist()
            break

    st.subheader(f"Texas Lotto Winning Numbers: {', '.join(map(str, sorted(st.session_state['winning_numbers'])))}")
    st.space()

    center_config = {col: st.column_config.Column(alignment="center") for col in st.session_state['user_df'].columns}
    styled_df = st.session_state['user_df'].style.map(lambda val: "background-color: green; color: white;" if val in st.session_state['winning_numbers'] else "")
    st.dataframe(styled_df, column_config=center_config, hide_index=True)

# Main function
def main():
    # Downloads the latest Lotto Texas CSV file if it doesn't exist in the session state
    if "csv_df" not in st.session_state:
        # Fetch the content from the URL
        response = requests.get(url)

        # Save the content to a local file
        with open(csv_file, "wb") as file:
            file.write(response.content)

        # Load the CSV file, narrows down to the last 50 rows, renames the dataframe's columns, combines the Month, Day, and Year columns into a single Draw Date column, and drops the original Month, Day, and Year columns
        st.session_state['csv_df'] = pd.read_csv(csv_file, encoding="utf-8", header=None)
        st.session_state['csv_df'] = st.session_state['csv_df'].tail(50)
        st.session_state['csv_df'].rename(columns={0: "Draw Date", 1: "Month", 2: "Day", 3: "Year", 4: "Num1", 5: "Num2", 6: "Num3", 7: "Num4", 8: "Num5", 9: "Num6"}, inplace=True)
        st.session_state['csv_df']['Draw Date'] = st.session_state['csv_df']['Month'].astype(str) + "/" + st.session_state['csv_df']['Day'].astype(str) + "/" + st.session_state['csv_df']['Year'].astype(str)
        st.session_state['csv_df'] = st.session_state['csv_df'].drop(st.session_state['csv_df'].columns[[1, 2, 3]], axis=1)

        # Initializes the winning_numbers list in the session state
        st.session_state['winning_numbers'] = []

    # Loads the user numbers from the numbers.json file if they don't exist in the session state
    if "user_df" not in st.session_state:
        # Open the numbers.json file and load the data
        with open(f'{project_dir}/numbers.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        user_numbers = []

        for d in data:
            user_numbers.append(d)

        st.session_state['user_df'] = pd.DataFrame(user_numbers, columns=["Num 1", "Num 2", "Num 3", "Num 4", "Num 5", "Num 6"])

    # Creates a sidebar for selecting the drawing date
    with st.sidebar:
        st.header("Select a Drawing Date")
        st.sidebar.selectbox("Drawing Date", options=st.session_state['csv_df'].iloc[::-1, 0].tolist(), key="selected_date") 

        st.space("large")
        st.divider()
        st.space("large")

        if ticket_image_path and Path(ticket_image_path).exists():
            image = Image.open(ticket_image_path)
            image = ImageOps.exif_transpose(image)
            st.image(image, caption="Current ticket", width='stretch')

        uploaded_file = st.file_uploader(label="Upload an image from your computer or phone", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image = ImageOps.exif_transpose(image)  
            image.save(ticket_image_path)
            st.rerun()

    get_winning_numbers()

if __name__ == "__main__":
    main()
    print(f"\n----------------------------")
    