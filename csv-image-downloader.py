import csv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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
                    return img_filename
                
                img_response = requests.get(img_url, headers=headers, timeout=10)
                img_response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Imagem baixada com sucesso: {img_filename}")
                return img_filename
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

def process_csv(input_file, output_path):
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Lendo arquivo de entrada: {input_file}")
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        total_rows = sum(1 for row in csvfile) - 1  # Count total rows (excluding header)
        csvfile.seek(0)  # Reset file pointer
        next(reader)  # Skip header row
        
        for i, row in enumerate(reader, 1):
            print(f"\nProcessando linha {i} de {total_rows}")
            city_code = row['Sigla da Cidade']
            slug = row['Slug da Empresa']
            
            if slug:
                url = f'https://ix.br/trafego/pix/{city_code}/{slug}/bps'
                downloaded_image = download_image(url, output_path)
                if downloaded_image:
                    print(f"Imagem para {slug} baixada: {downloaded_image}")
                else:
                    print(f"Falha ao baixar imagem para {slug}")
            else:
                print("Slug da empresa não disponível, pulando download da imagem")

if __name__ == '__main__':
    input_file = 'output/empresas_ix_br.csv'
    output_path = 'output/img'
    process_csv(input_file, output_path)
    print(f"Download de imagens concluído. As imagens foram salvas em: {output_path}")
