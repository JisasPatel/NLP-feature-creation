#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 00:08:21 2023

@author: jisaspatel
"""

import streamlit as st
import pandas as pd
import app

def main():
    st.title("Excel File Reader")

    # Upload the Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        result = app.from_Df(df) 
        st.dataframe(result)

if __name__ == "__main__":
    main()
