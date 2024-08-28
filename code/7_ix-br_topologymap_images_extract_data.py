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
API_CALL_DELAY = 1  # seconds

# Initialize the ChatOpenAI model
chat = ChatOpenAI(model="gpt-4o-mini", max_tokens=300)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path):
    base64_image = encode_image(image_path)
    
    messages = [
        SystemMessage(content="You are an AI assistant that analyzes topology map images and extracts specific data from them."),
        HumanMessage(content=[
            {"type": "text", "text": "Extract the following data from this topology map image:\n"
             "PIX-A: <name>\n"
             "Download_valor: <value><unit>\n"
             "Download_porcentagem: <percentage>%\n"
             "Upload_valor: <value><unit>\n"
             "Upload_porcentagem: <percentage>%\n"
             "PIX-B: <name>\n"
             "Where <name> is the name of the PIX, <value> is a number, <unit> is K, M, G, or T, and <percentage> is a number.\n"
             "If percentage is not available in the image, use the value from the legend based on the arrow color.\n"
             "If there are multiple connections, provide data for the one with the highest download value.\n"
             "For 1-to-N or 1-to-'PIX Central' topologies, focus on the main connection.\n"
             "Respond only with the extracted data in the exact format specified, nothing else."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ])
    ]
    
    response = chat(messages)
    return response.content

def update_csv(df, extracted_data, city_code):
    lines = extracted_data.strip().split('\n')
    data = {}
    for line in lines:
        parts = line.split(': ', 1)
        if len(parts) == 2:
            key, value = parts
            data[key] = value
        else:
            logging.warning(f"Linha inesperada na resposta da API para {city_code}: {line}")
    
    update_data = {
        'Sigla da Cidade': city_code,
        'PIX-A': data.get('PIX-A', ''),
        'Download_valor': data.get('Download_valor', ''),
        'Download_porcentagem': data.get('Download_porcentagem', ''),
        'Upload_valor': data.get('Upload_valor', ''),
        'Upload_porcentagem': data.get('Upload_porcentagem', ''),
        'PIX-B': data.get('PIX-B', ''),
        'Extraction_Date': date.today().isoformat()
    }
    
    df.loc[df['Sigla da Cidade'] == city_code, update_data.keys()] = update_data.values()
    return df

def is_row_processed(row):
    return pd.notna(row['PIX-A']) and pd.notna(row['PIX-B']) and \
           row['PIX-A'] != '' and row['PIX-B'] != '' and \
           pd.notna(row['Download_valor']) and pd.notna(row['Upload_valor'])

def process_single_image(args):
    index, row, image_dir = args
    city_code = row['Sigla da Cidade']
    image_path = os.path.join(image_dir, f"topologymap__{city_code.lower()}.png")
    
    logging.info(f"Processando imagem para {city_code}")
    
    if is_row_processed(row):
        logging.info(f"Linha já processada para {city_code}. Pulando.")
        return index, None, "skipped"
    
    if not os.path.exists(image_path):
        logging.error(f"Imagem não encontrada para {city_code}: {image_path}")
        return index, None, "error"
    
    logging.info(f"Imagem encontrada para {city_code}: {image_path}")
    
    for attempt in range(MAX_RETRIES):
        try:
            extracted_data = process_image(image_path)
            time.sleep(API_CALL_DELAY)  # Adiciona um atraso entre as chamadas da API
            return index, extracted_data, "success"
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                return index, None, f"error: {str(e)}"
            time.sleep(RETRY_DELAY)

def main():
    input_csv_path = "output/ix-br_slugs_data.csv"
    output_csv_path = "output/ix-br_topologymaps_data.csv"
    image_dir = "output/img/topologymap"

    if os.path.exists(output_csv_path):
        logging.info(f"Arquivo CSV de saída já existe. Lendo de {output_csv_path}")
        df = pd.read_csv(output_csv_path)
    else:
        logging.info(f"Arquivo CSV de saída não existe. Lendo de {input_csv_path}")
        df = pd.read_csv(input_csv_path)
        new_columns = ['PIX-A', 'Download_valor', 'Download_porcentagem',
                       'Upload_valor', 'Upload_porcentagem', 'PIX-B',
                       'Extraction_Date']
        for col in new_columns:
            if col not in df.columns:
                df[col] = pd.NA

    logging.info(f"Total de linhas no DataFrame: {len(df)}")
    logging.info(f"Colunas no DataFrame: {df.columns.tolist()}")

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
                df = update_csv(df, extracted_data, df.loc[index, 'Sigla da Cidade'])
                processed_images += 1
            elif status == "skipped":
                skipped_images += 1
            else:
                logging.error(f"Error processing image for {df.loc[index, 'Sigla da Cidade']}: {extracted_data}")
                errors += 1
            
            if processed_images % 10 == 0:
                df.to_csv(output_csv_path, index=False)
                logging.info(f"CSV file saved. Processed: {processed_images}, Skipped: {skipped_images}, Errors: {errors}")

    df.to_csv(output_csv_path, index=False)
    logging.info(f"Processing complete. Total images: {total_images}, Processed: {processed_images}, Skipped: {skipped_images}, Errors: {errors}")
    logging.info(f"CSV file updated: {output_csv_path}")

if __name__ == "__main__":
    main()
