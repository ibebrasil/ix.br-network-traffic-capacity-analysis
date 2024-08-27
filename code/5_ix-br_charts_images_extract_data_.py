import os
import csv
from datetime import date
import base64
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import pandas as pd
import time
import logging
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Please check your .env file.")

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
MAX_WORKERS = 4  # Number of parallel processes

# Initialize the ChatOpenAI model
chat = ChatOpenAI(model="gpt-4o-mini", max_tokens=300)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path):
    base64_image = encode_image(image_path)
    
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes images and extracts specific data from them."),
        HumanMessage(content=[
            {"type": "text", "text": "Extract the following data from this image:\n"
             "Input Maximum: <value> <unit> Average: <value> <unit> Current: <value> <unit>\n"
             "Output Maximum: <value> <unit> Average: <value> <unit> Current: <value> <unit>\n"
             "Where <value> is a decimal number with two decimal places and <unit> is usually 'Gbps'.\n"
             "Respond only with the extracted data in the exact format specified, nothing else."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ])
    ]
    
    response = chat(messages)
    return response.content

def update_csv(df, extracted_data, slug):
    lines = extracted_data.strip().split('\n')
    input_data = lines[0].split()
    output_data = lines[1].split()
    
    update_data = {
        'Input_Maximum': input_data[2],
        'Input_Maximum_Unit': input_data[3],
        'Input_Average': input_data[5],
        'Input_Average_Unit': input_data[6],
        'Input_Current': input_data[8],
        'Input_Current_Unit': input_data[9],
        'Output_Maximum': output_data[2],
        'Output_Maximum_Unit': output_data[3],
        'Output_Average': output_data[5],
        'Output_Average_Unit': output_data[6],
        'Output_Current': output_data[8],
        'Output_Current_Unit': output_data[9],
        'Extraction_Date': date.today().isoformat()
    }
    
    df.loc[df['Slug'] == slug, update_data.keys()] = update_data.values()
    return df

def is_row_processed(row):
    return pd.notna(row['Input_Maximum']) and pd.notna(row['Output_Maximum']) and \
           row['Input_Maximum'] != '' and row['Output_Maximum'] != ''

def process_single_image(args):
    index, row, image_dir = args
    slug = row['Slug']
    city_code = row['Sigla da Cidade']
    image_path = os.path.join(image_dir, f"pix__{city_code}__{slug}__bps__daily.png")
    
    if is_row_processed(row):
        return index, None, "skipped"
    
    if not os.path.exists(image_path):
        return index, None, "error"
    
    for attempt in range(MAX_RETRIES):
        try:
            extracted_data = process_image(image_path)
            return index, extracted_data, "success"
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                return index, None, f"error: {str(e)}"
            time.sleep(RETRY_DELAY)

def main():
    input_csv_path = "output/ix-br_slugs_data.csv"
    output_csv_path = "output/ix-br_slugs_data_processed.csv"
    image_dir = "output/img/"

    if os.path.exists(output_csv_path):
        logging.info(f"Output CSV file already exists. Reading from {output_csv_path}")
        df = pd.read_csv(output_csv_path)
    else:
        logging.info(f"Output CSV file does not exist. Reading from {input_csv_path}")
        df = pd.read_csv(input_csv_path)
        new_columns = ['Input_Maximum', 'Input_Maximum_Unit', 'Input_Average', 'Input_Average_Unit',
                       'Input_Current', 'Input_Current_Unit', 'Output_Maximum', 'Output_Maximum_Unit',
                       'Output_Average', 'Output_Average_Unit', 'Output_Current', 'Output_Current_Unit',
                       'Extraction_Date']
        for col in new_columns:
            if col not in df.columns:
                df[col] = pd.NA

    total_images = len(df)
    logging.info(f"Starting processing of {total_images} images...")

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_image, (index, row, image_dir)) for index, row in df.iterrows()]
        
        processed_images = 0
        skipped_images = 0
        errors = 0
        
        for future in tqdm(as_completed(futures), total=total_images, desc="Processing Images"):
            index, extracted_data, status = future.result()
            if status == "success":
                df = update_csv(df, extracted_data, df.loc[index, 'Slug'])
                processed_images += 1
            elif status == "skipped":
                skipped_images += 1
            else:
                errors += 1
            
            if processed_images % 10 == 0:
                df.to_csv(output_csv_path, index=False)
                logging.info(f"CSV file saved. Processed: {processed_images}, Skipped: {skipped_images}, Errors: {errors}")

    df.to_csv(output_csv_path, index=False)
    logging.info(f"Processing complete. Total images: {total_images}, Processed: {processed_images}, Skipped: {skipped_images}, Errors: {errors}")
    logging.info(f"CSV file updated: {output_csv_path}")

if __name__ == "__main__":
    main()
