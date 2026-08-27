# Imports
from pathlib import Path
from PIL import Image, ImageOps
import json
import os
import pandas as pd
import requests
import streamlit as st

# Gets the directory of the currently running script and sets the current ticket image path
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Texas Lotto CSV URL and project file paths
url = "https://www.texaslottery.com/export/sites/lottery/Games/Lotto_Texas/Winning_Numbers/lottotexas.csv"
csv_file = f'{DATA_DIR}/texas-lotto.csv'

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
        with open(f'{PROJECT_DIR}/numbers.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        user_numbers = []

        for d in data:
            user_numbers.append(d)

        st.session_state['user_df'] = pd.DataFrame(user_numbers, columns=["Num 1", "Num 2", "Num 3", "Num 4", "Num 5", "Num 6"])

    # Creates a sidebar for selecting the drawing date
    with st.sidebar:
        st.header("Select a Drawing Date")
        st.sidebar.selectbox("Drawing Date", options=st.session_state['csv_df'].iloc[::-1, 0].tolist(), key="selected_date") 

        with st.sidebar.container(key="sidebar_bottom"):
            uploaded_file = st.file_uploader("Upload lottery ticket", type=["jpg", "jpeg", "png"])

            if uploaded_file is not None:
                for ext in ["jpg", "jpeg", "png"]:
                    old_file = DATA_DIR / f"lotto_ticket.{ext}"
                    if old_file.exists():
                        old_file.unlink()

                image = Image.open(uploaded_file)
                image = ImageOps.exif_transpose(image)

                if image.format == "PNG":
                    output_path = DATA_DIR / "lotto_ticket.png"
                    image.save(output_path, format="PNG")
                else:
                    if image.mode != "RGB":
                        image = image.convert("RGB")

                    output_path = DATA_DIR / "lotto_ticket.jpg"
                    image.save(output_path, format="JPEG", quality=95)

            ticket_file = list(DATA_DIR.glob("lotto_ticket.*"))

            if ticket_file:
                st.image(str(ticket_file[0]), caption="Current Lottery Ticket", width="stretch")
            else:
                st.info("No lottery ticket has been uploaded.")

        
            st.caption("© Tim's App")

            # Inject CSS to position that specific container at the bottom
            st.html("""
                <style>
                .st-key-sidebar_bottom {
                    position: absolute;
                    bottom: 20px;
                    left: 0;
                    right: 0;
                    padding: 0 1rem;
                }
                </style>
            """)


    get_winning_numbers()

if __name__ == "__main__":
    main()
    print(f"\n----------------------------")
    