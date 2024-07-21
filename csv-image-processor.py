import csv
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
import re
from datetime import date
from urllib.parse import urljoin
import cv2
import numpy as np
import time

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def download_image(url, output_path, retries=MAX_RETRIES):
    print(f"Verificando imagem de: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            monthly_img = soup.find('img', alt='Monthly')
            if monthly_img:
                img_url = urljoin(url, monthly_img['src'])
                img_filename = os.path.basename(img_url)
                img_path = os.path.join(output_path, img_filename)
                
                if os.path.exists(img_path):
                    print(f"Imagem já existe: {img_filename}. Pulando download.")
                    with open(img_path, 'rb') as f:
                        return f.read()
                
                img_response = requests.get(img_url, headers=headers, timeout=10)
                img_response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Imagem baixada com sucesso: {img_filename}")
                return img_response.content
            else:
                print(f"Imagem mensal não encontrada em: {url}")
                return None
        except requests.RequestException as e:
            print(f"Tentativa {attempt + 1} falhou. Erro: {e}")
            if attempt < retries - 1:
                print(f"Tentando novamente em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Todas as {retries} tentativas falharam para {url}")
                return None

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, thresh = cv2.threshold(denoised, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_value(image, x, y, w, h):
    roi = image[y:y+h, x:x+w]
    text = pytesseract.image_to_string(roi, config='--psm 7 -c tessedit_char_whitelist=0123456789.GMbps')
    return text.strip()

def extract_ocr_data(image_content, retries=MAX_RETRIES):
    if image_content is None:
        return None

    for attempt in range(retries):
        try:
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            processed_img = preprocess_image(img)
            
            height, width = processed_img.shape
            
            # Definir regiões de interesse (ROI) para cada valor
            rois = {
                'Input_Maximum':  (width // 2 - 200, height - 60, 200, 20),
                'Input_Average':  (width // 2 - 200, height - 40, 200, 20),
                'Input_Current':  (width // 2 - 200, height - 20, 200, 20),
                'Output_Maximum': (width // 2 + 50, height - 60, 200, 20),
                'Output_Average': (width // 2 + 50, height - 40, 200, 20),
                'Output_Current': (width // 2 + 50, height - 20, 200, 20),
            }
            
            results = {}
            for key, (x, y, w, h) in rois.items():
                value = extract_value(processed_img, x, y, w, h)
                if value:
                    results[key] = value
                else:
                    print(f"Falha ao extrair {key}")
            
            if len(results) == 6:
                return results
            else:
                print(f"Tentativa {attempt + 1}: Não foi possível extrair todos os valores necessários")
                if attempt < retries - 1:
                    print(f"Tentando novamente em {RETRY_DELAY} segundos...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"Todas as {retries} tentativas falharam para extrair dados OCR")
                    return None
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou. Erro ao processar imagem: {e}")
            if attempt < retries - 1:
                print(f"Tentando novamente em {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Todas as {retries} tentativas falharam para processar a imagem")
                return None

def process_csv(input_file, output_file):
    os.makedirs('output/img', exist_ok=True)
    
    print(f"Lendo arquivo de entrada: {input_file}")
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames + [
            'Input_Maximum', 'Input_Average', 'Input_Current',
            'Output_Maximum', 'Output_Average', 'Output_Current',
            'Data_de_Extracao'
        ]
        
        rows = []
        total_rows = sum(1 for row in csvfile)  # Count total rows
        csvfile.seek(0)  # Reset file pointer
        next(reader)  # Skip header row
        
        for i, row in enumerate(reader, 1):
            print(f"\nProcessando linha {i} de {total_rows-1}")
            city_code = row['Sigla da Cidade']
            slug = row['Slug da Empresa']
            
            if slug:
                url = f'https://ix.br/trafego/pix/{city_code}/{slug}/bps'
                image_content = download_image(url, 'output/img')
                ocr_data = extract_ocr_data(image_content) if image_content else None
                
                if ocr_data:
                    row.update(ocr_data)
                else:
                    print("Dados OCR não disponíveis, preenchendo com 'N/A'")
                    for key in ['Input_Maximum', 'Input_Average', 'Input_Current', 'Output_Maximum', 'Output_Average', 'Output_Current']:
                        row[key] = 'N/A'
            else:
                print("Slug da empresa não disponível, pulando download da imagem")
                for key in ['Input_Maximum', 'Input_Average', 'Input_Current', 'Output_Maximum', 'Output_Average', 'Output_Current']:
                    row[key] = 'N/A'
            
            row['Data_de_Extracao'] = str(date.today())
            rows.append(row)
    
    print(f"\nEscrevendo dados atualizados em: {output_file}")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    input_file = 'output/empresas_ix_br.csv'
    output_file = 'output/empresas_ix_br_updated.csv'
    process_csv(input_file, output_file)
    print(f"Processamento concluído. Dados atualizados salvos em: {output_file}")
