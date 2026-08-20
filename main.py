# Imports
import csv
import json
import os
import pandas as pd
import requests
import streamlit as st

# Gets the directory of the currently running script
project_dir = os.path.dirname(os.path.abspath(__file__))

# Texas Lotto CSV URL and local file path
url = "https://www.texaslottery.com/export/sites/lottery/Games/Lotto_Texas/Winning_Numbers/lottotexas.csv"
file_path = "C:/Users/timwd/OneDrive/Documents/CSV/texas-lotto.csv"
user_numbers = []
winning_numbers = []

# Main function
def main():
    st.title("Texas Lotto Winning Numbers")
    
    # Fetch the content from the URL
    response = requests.get(url)

    # Save the content to a local file
    with open(file_path, "wb") as file:
        file.write(response.content)

    with open(file_path, "r", encoding="utf-8") as file:
        final_line = file.readlines()[-1]

    st.write(final_line)

    # Open the file and load the data
    with open(f'{project_dir}/numbers.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for d in data:
        user_numbers.append(d)

    user_df = pd.DataFrame(user_numbers, columns=["0", "1", "2", "3", "4", "5"])
    center_config = {col: st.column_config.Column(alignment="center") for col in user_df.columns}

    styled_df = user_df.style.map(lambda val: "background-color: green; color: white;" if val == 9 else "")

    st.dataframe(styled_df, column_config=center_config, hide_index=True)

if __name__ == "__main__":
    main()
    print(f"\n----------------------------")
    