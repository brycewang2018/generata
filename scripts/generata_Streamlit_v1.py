import streamlit as st
import openai
import pandas as pd
from io import BytesIO
import json

# Streamlit App
st.title("Tabular Data Generator using OpenAI GPT-4")

# Step 1: Input API Key
api_key = st.text_input("Enter your OpenAI API Key", type="password")

if api_key:
    openai.api_key = api_key
    st.success("API Key set successfully!")

    # Step 2: User Input for Data Requirements
    st.header("Define Your Data Requirements")
    columns = st.text_area("Enter column names and types (e.g., 'age:int, name:string, salary:float')")
    row_count = st.number_input("Enter number of rows", min_value=1, value=10, step=1)
    output_format = st.selectbox("Select output format", ["CSV", "XLSX"])

    if st.button("Generate Data"):
        if not columns:
            st.error("Please specify column names and types.")
        else:
            # Parse the columns input
            try:
                col_definitions = [col.strip() for col in columns.split(',')]
                column_details = {col.split(':')[0]: col.split(':')[1] for col in col_definitions}
            except Exception as e:
                st.error("Invalid column definition format. Use 'name:type'.")
                st.stop()

            # Generate prompt for GPT-4
            prompt = (
                f"Generate a tabular dataset with {row_count} rows based on the following columns: "
                f"{json.dumps(column_details)}. Provide the data in JSON format."
            )

            # Call OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data generator."},
                        {"role": "user", "content": prompt}
                    ]
                )

                generated_data = response['choices'][0]['message']['content']
                data = pd.read_json(BytesIO(generated_data.encode('utf-8')))

                # Output results
                st.success("Data generated successfully!")
                st.write(data)

                # Save file
                if output_format == "CSV":
                    csv_data = data.to_csv(index=False)
                    st.download_button("Download CSV", csv_data, "generated_data.csv", "text/csv")
                elif output_format == "XLSX":
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        data.to_excel(writer, index=False, sheet_name='Sheet1')
                    xlsx_data = output.getvalue()
                    st.download_button("Download XLSX", xlsx_data, "generated_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            except Exception as e:
                st.error(f"Error generating data: {e}")
