import urllib.request
import pandas as pd
import re
from PyPDF2 import PdfReader
import io
import ssl
import streamlit as st


def loadpdf(url):
    """Fetches the PDF from the URL."""
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Disable SSL verification
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context) as response:
            data = response.read()
        return io.BytesIO(data)

    except urllib.error.HTTPError as e:
        st.error(f"Failed to fetch data from {url} - HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error while fetching PDF: {e}")
        return None



def extract(file_path):
    """Extract incidents from the PDF and return as a DataFrame."""
    try:
        reader = PdfReader(file_path)
        incident_records = []

        for page in reader.pages:
            text = page.extract_text()
            rows = text.split("\n")

            current_record = {}
            for row in rows:
                row = row.strip()
                if not row or 'NORMAN POLICE DEPARTMENT' in row or 'Daily Arrest Activity' in row:
                    continue

                # Extract Date and Time
                date_match = re.match(r'(\d{1,2}/\d{1,2}/\d{4}) (\d{2}:\d{2})', row)
                if date_match:
                    if current_record:
                        incident_records.append(current_record)
                        current_record = {}

                    current_record['Date'] = date_match.group(1)
                    current_record['Time'] = date_match.group(2)

                # Extract Case Number
                case_number_match = re.search(r'(\d{8})', row)
                if case_number_match:
                    current_record['Case Number'] = f"2024-{case_number_match.group(1)}"

                # Extract Arrest Location (Column 3) and Offense (Column 4)
                columns = row.split()
                if len(columns) >= 4:
                    current_record['Arrest Location'] = columns[2]  # Third column
                    current_record['Offense'] = columns[3]          # Fourth column

            # Append the last record
            if current_record:
                incident_records.append(current_record)

        # Convert records to a DataFrame
        df = pd.DataFrame(incident_records)

        # Ensure all expected columns are present
        for col in ['Date', 'Time', 'Case Number', 'Arrest Location', 'Offense']:
            if col not in df.columns:
                df[col] = None

        # Drop rows where Date, Time, or Case Number is missing
        df.dropna(subset=['Date', 'Time', 'Case Number'], inplace=True)

        return df[['Date', 'Time', 'Case Number', 'Arrest Location', 'Offense']]

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise



