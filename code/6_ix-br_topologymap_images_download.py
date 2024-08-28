import csv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def download_topology_map(url, output_path, city_code, retries=MAX_RETRIES):
    print(f"Verificando mapa de topologia da cidade: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            img = soup.find('img', attrs={'usemap': '#map'})
            if img:
                img_url = urljoin(url, img['src'])
                img_filename = f"topologymap__{city_code.lower()}.png"
                img_path = os.path.join(output_path, img_filename)
                
                if os.path.exists(img_path):
                    print(f"Mapa de topologia já existe: {img_filename}. Pulando download.")
                    return img_filename
                
                img_response = requests.get(img_url, headers=headers, timeout=10)
                img_response.raise_for_status()
                
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Mapa de topologia baixado com sucesso: {img_filename}")
                return img_filename
            else:
                print(f"Mapa de topologia não encontrado em: {url}")
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
            
            url = f'https://ix.br/trafego/pix/{city_code}'
            downloaded_map = download_topology_map(url, output_path, city_code)
            if downloaded_map:
                print(f"Mapa de topologia para {city_code} baixado: {downloaded_map}")
            else:
                print(f"Falha ao baixar mapa de topologia para {city_code}")

if __name__ == '__main__':
    input_file = 'output/ix-br_slugs_data.csv'
    output_path = 'output/img/topologymap'
    process_csv(input_file, output_path)
    print(f"Download de mapas de topologia das cidades concluído. Os mapas foram salvos em: {output_path}")
