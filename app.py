
import streamlit as st
import os
import pandas as pd
from tempfile import NamedTemporaryFile
import camelot
import tabula
import numpy as np
import fitz  # PyMuPDF
import requests
from pdf2image import convert_from_path
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType

import os.path
import zipfile
import json
import logging
import tempfile

def pdf_processing_page():
    st.title("PDF Processing App")
    
    # Description
    st.markdown("**Note:** Do not select both 'Adobe' and 'Nanonet' methods for processing at the same time.")
    
    # Upload PDF file
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if pdf_file:
        # Read PDF and perform processing based on dropdown selection
        processing_method = st.selectbox("Select a processing method:", ["Camelot Stream", "Camelot Lattice", "Tabula", "Nanonet", "Adobe"])
        
        if processing_method == "Camelot Stream":
            processed_data = process_with_camelot(pdf_file, flavor="stream")
        elif processing_method == "Camelot Lattice":
            processed_data = process_with_camelot(pdf_file, flavor="lattice")
        elif processing_method == "Tabula":
            processed_data = process_with_tabula(pdf_file)
        elif processing_method == "Nanonet":
            page_number = st.number_input("Enter the page number to process:", min_value=1, value=1)
            processed_data = process_with_nanonets(pdf_file, int(page_number))
        elif processing_method == "Adobe":
            page_number_from = st.number_input("Starting:", min_value=1, value=1)
            page_number_to = st.number_input("Ending:", min_value=1, value=1)
            processed_data = process_with_adobe(pdf_file, int(page_number_from), int(page_number_to))
        
        # Create a temporary Excel file
        with NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file.close()
            save_to_excel(processed_data, temp_file.name)
        
        # Display the download link
        with open(temp_file.name, "rb") as file:
            st.download_button("Download Processed Excel", file.read(), file_name=temp_file.name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Clean up temporary Excel file
        os.remove(temp_file.name)

def feedback_page():
    st.title("Feedback Page")
    
    # Add your feedback form or content here
    st.write("Please provide your feedback on the PDF Processing App.")

def main():
    st.title("PDF Processing App")
    
    # Description
    st.markdown("**Note:** Do not select both 'Adobe' and 'Nanonet' methods for processing at the same time.")
    
    # Upload PDF file
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if pdf_file:
        # Read PDF and perform processing based on dropdown selection
        processing_method = st.selectbox("Select a processing method:", ["Camelot Stream", "Camelot Lattice", "Tabula", "Nanonet", "Adobe"])
        
        if processing_method == "Camelot Stream":
            processed_data = process_with_camelot(pdf_file, flavor="stream")
        elif processing_method == "Camelot Lattice":
            processed_data = process_with_camelot(pdf_file, flavor="lattice")
        elif processing_method == "Tabula":
            processed_data = process_with_tabula(pdf_file)
        elif processing_method == "Nanonet":
            page_number = st.number_input("Enter the page number to process:", min_value=1, value=1)
            processed_data = process_with_nanonets(pdf_file, int(page_number))
        elif processing_method == "Adobe":
            page_number_from = st.number_input("Starting:", min_value=1, value=1)
            page_number_to = st.number_input("Ending:", min_value=1, value=1)
            processed_data = process_with_adobe(pdf_file, int(page_number_from), int(page_number_to))
        
        # Create a temporary Excel file
        with NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file.close()
            save_to_excel(processed_data, temp_file.name)
        
        # Display the download link
        with open(temp_file.name, "rb") as file:
            st.download_button("Download Processed Excel", file.read(), file_name=temp_file.name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Clean up temporary Excel file
        os.remove(temp_file.name)

def save_to_excel(processed_data, excel_path):
    # Create ExcelWriter object
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    
    # Loop through tables and save each in a new sheet
    for i, table in enumerate(processed_data, start=1):
        sheet_name = f"Table_{i}"
        table.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Save the Excel file
    writer.close()

def process_with_camelot(pdf_file, flavor):
    # Save the uploaded PDF to a temporary file
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.read())
    
    # Read PDF using Camelot with the selected flavor
    tables = camelot.read_pdf(temp_pdf_path, pages="all", flavor=flavor)
    
    # Create a list of DataFrames
    df_list = [table.df for table in tables]
    
    # Clean up temporary PDF file
    os.remove(temp_pdf_path)
    
    return df_list

def process_with_tabula(pdf_file):
    # Save the uploaded PDF to a temporary file
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.read())
    
    # Read PDF using Tabula
    tables = tabula.read_pdf(temp_pdf_path, pages="all", multiple_tables=True)
    
    # Create a list of DataFrames
    df_list = [table for table in tables]
    
    # Clean up temporary PDF file
    os.remove(temp_pdf_path)
    
    return df_list


def process_with_nanonets(pdf_file, page_number):
    # Convert the selected PDF page to an image
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.read())
    
    # Convert the selected PDF page to an image
    images = convert_from_path(temp_pdf_path, first_page=page_number, last_page=page_number)
    image = images[0]
    
    # Temporary file to save the image
    image_temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
    image.save(image_temp_file, "JPEG")
    image_temp_file.close()
    
    # TODO: Call the function nanonet_pdf_convert with the image_temp_file and return the processed data
    processed_data = nanonet_pdf_convert(image_temp_file.name)
    
    # Clean up temporary files
    os.remove(temp_pdf_path)
    os.remove(image_temp_file.name)
    
    return processed_data

def nanonet_pdf_convert(image_file_path):
    url = 'https://app.nanonets.com/api/v2/OCR/Model/dbb69085-b341-4e4d-826b-7ead8bd751da/LabelFile/?async=false'
    data = {'file': open(image_file_path, 'rb')}

    # Make a request to the Nanonets API
    response = requests.post(url, auth=requests.auth.HTTPBasicAuth('e3a2dfc1-2f96-11ee-a3ff-ae9ef8a92e23', ''), files=data)

    alldfs = []
    for item in response.json()["result"]:
        tables = []

        for pred in item['prediction']:
            if pred['type'] == 'table':
                labels = ['none'] * 100

            maxcol = 0
            for cell in pred['cells']:
                if labels[cell['col'] - 1] == 'none':
                    labels[cell['col'] - 1] = cell['label']
                    if cell['col'] > maxcol:
                        maxcol = cell['col']

            labels = labels[:maxcol]

            df = pd.DataFrame(index=np.arange(100), columns=np.arange(100))

            for cell in pred['cells']:
                df[cell['col']][cell['row']] = cell['text']

            df = df.dropna(axis=0, how='all')
            df = df.dropna(axis=1, how='all')
            df.columns = labels
            tables.append(df)

        alldfs.append(tables)
    
    # Create a list of DataFrames from alldfs
    df_list = [df for table in alldfs for df in table]
    
    return df_list


def extract_page_from_pdf(pdf_document, page_number_from, page_number_to):
    try:
        new_pdf_document = fitz.open()
        new_pdf_document.insert_pdf(pdf_document, from_page=page_number_from - 1, to_page=page_number_to - 1)
        
        return new_pdf_document

    except Exception as e:
        print(f"Error extracting single page: {str(e)}")
        return None
    
def single_page_pdf(pdf_path):
    cl_id = 'e027be720cbc4c199f2661edcd03fcab'
    cl_secret = 'p8e-j2U2hMesGn8X9KNhKraeNkLz8btX3t0B'

    try:
        # Initial setup, create credentials instance.
        credentials = Credentials.service_principal_credentials_builder().with_client_id(cl_id).with_client_secret(cl_secret).build()

        # Create an ExecutionContext using credentials and create a new operation instance.
        execution_context = ExecutionContext.create(credentials)
        extract_pdf_operation = ExtractPDFOperation.create_new()

        # Set operation input from a source file.
        source = FileRef.create_from_local_file(pdf_path)
        extract_pdf_operation.set_input(source)

        # Build ExtractPDF options and set them into the operation
        extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
            .with_element_to_extract(ExtractElementType.TABLES).build()
        extract_pdf_operation.set_options(extract_pdf_options)

        # Execute the operation.
        result: FileRef = extract_pdf_operation.execute(execution_context)

        # Save the result to a temporary location.
        temp_dir = tempfile.TemporaryDirectory()
        temp_zip_file = os.path.join(temp_dir.name, "extracted_tables.zip")
        result.save_as(temp_zip_file)

        alldfs = []

        with zipfile.ZipFile(temp_zip_file, 'r') as archive:
            tables_folder = "tables"
            for excel_file_name in archive.namelist():
                if excel_file_name.startswith(tables_folder) and excel_file_name.endswith(".xlsx"):
                    with archive.open(excel_file_name) as excel_file:
                        df = pd.read_excel(excel_file)
                        alldfs.append(df)
        
        # Clean up the temporary directory after processing
        temp_dir.cleanup()
        
        return alldfs

    except (ServiceApiException, ServiceUsageException, SdkException):
        logging.exception("Exception encountered while executing operation")
        return []
    
def process_with_adobe(pdf_path, page_number_from, page_number_to):
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(pdf_path.read())

    pdf_document = fitz.open(temp_pdf_path)
    extracted_pdf = extract_page_from_pdf(pdf_document, page_number_from, page_number_to)
    
    alldfs = []
    
    if extracted_pdf:
        # Create a temporary directory to store the extracted PDF
        with tempfile.TemporaryDirectory() as temp_extracted_dir:
            temp_extracted_pdf_path = os.path.join(temp_extracted_dir, "extracted_pdf.pdf")
            
            # Save the extracted PDF to the temporary location
            extracted_pdf.save(temp_extracted_pdf_path)
            
            # Call the single_page_pdf function to extract tables from the extracted PDF
            alldfs = single_page_pdf(temp_extracted_pdf_path)
            
            # Clean up the temporary extracted PDF
            extracted_pdf.close()
            os.remove(temp_extracted_pdf_path)
            
    # Clean up the PDF document
    pdf_document.close()
    
    return alldfs  # Return the extracted DataFrames or an empty list if no tables were extracted



if __name__ == "__main__":
    main()

