import os
import csv
from datetime import date
import base64
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import pandas as pd
import time

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Please check your .env file.")

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

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
    # Parse the extracted data
    lines = extracted_data.strip().split('\n')
    input_data = lines[0].split()
    output_data = lines[1].split()
    
    # Update the row
    row_index = df.index[df['Slug'] == slug].tolist()[0]
    df.at[row_index, 'Input_Maximum'] = input_data[2]
    df.at[row_index, 'Input_Maximum_Unit'] = input_data[3]
    df.at[row_index, 'Input_Average'] = input_data[5]
    df.at[row_index, 'Input_Average_Unit'] = input_data[6]
    df.at[row_index, 'Input_Current'] = input_data[8]
    df.at[row_index, 'Input_Current_Unit'] = input_data[9]
    df.at[row_index, 'Output_Maximum'] = output_data[2]
    df.at[row_index, 'Output_Maximum_Unit'] = output_data[3]
    df.at[row_index, 'Output_Average'] = output_data[5]
    df.at[row_index, 'Output_Average_Unit'] = output_data[6]
    df.at[row_index, 'Output_Current'] = output_data[8]
    df.at[row_index, 'Output_Current_Unit'] = output_data[9]
    df.at[row_index, 'Extraction_Date'] = date.today().isoformat()
    
    return df

def is_row_processed(row):
    return False  # Always process all rows

# Main execution
input_csv_path = "output/ix-br_slugs_data.csv"
output_csv_path = "output/ix-br_slugs_data_processed.csv"
image_dir = "output/img/"

# Read the CSV file
df = pd.read_csv(input_csv_path)

# Add new columns if they don't exist
new_columns = ['Input_Maximum', 'Input_Maximum_Unit', 'Input_Average', 'Input_Average_Unit',
               'Input_Current', 'Input_Current_Unit', 'Output_Maximum', 'Output_Maximum_Unit',
               'Output_Average', 'Output_Average_Unit', 'Output_Current', 'Output_Current_Unit',
               'Extraction_Date']
for col in new_columns:
    if col not in df.columns:
        df[col] = pd.NA

total_images = len(df)
processed_images = 0
skipped_images = 0
errors = 0

print(f"Starting processing of {total_images} images...")

for index, row in df.iterrows():
    slug = row['Slug']
    image_path = os.path.join(image_dir, f"pix_{slug}_bps-monthly.png")
    
    processed_images += 1
    print(f"\nProcessing image {processed_images}/{total_images}: {slug}")
    
    # Check if data already exists
    if is_row_processed(row):
        print(f"Data already exists for {slug}. Skipping...")
        skipped_images += 1
        continue
    
    if os.path.exists(image_path):
        for attempt in range(MAX_RETRIES):
            try:
                extracted_data = process_image(image_path)
                print(f"Extracted data for {slug}:")
                print(extracted_data)
                df = update_csv(df, extracted_data, slug)
                print(f"CSV updated for {slug}")
                
                # Save the updated DataFrame after each successful extraction
                df.to_csv(output_csv_path, index=False)
                break  # Exit the retry loop if successful
            except Exception as e:
                print(f"Error processing {slug} (Attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    errors += 1
                    print(f"Failed to process {slug} after {MAX_RETRIES} attempts.")
    else:
        print(f"Image not found for {slug}")
        errors += 1
    
    # Add a small delay to avoid hitting API rate limits
    time.sleep(1)

    # Print progress
    print(f"Progress: {processed_images}/{total_images} images processed. Skipped: {skipped_images}, Errors: {errors}")

print(f"\nProcessing complete. Total images: {total_images}, Processed: {processed_images}, Skipped: {skipped_images}, Errors: {errors}")
print(f"New CSV file created: {output_csv_path}")
