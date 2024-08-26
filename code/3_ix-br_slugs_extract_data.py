import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re

def get_city_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    select = soup.find('select', {'id': 'router'})
    
    if not select:
        print("Não foi possível encontrar o elemento select com id 'router' na página.")
        return []
    
    options = select.find_all('option')
    city_info = []
    for option in options:
        if option.get('value'):
            value = option['value']
            city_uf = option.text.strip()
            city_code = value
            city_info.append((city_code, city_uf))
    
    return city_info

def get_company_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text

def extract_map_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    map_tag = soup.find('map')
    
    if not map_tag:
        print("Não foi possível encontrar a tag 'map' na página.")
        return []
    
    companies = []
    for area in map_tag.find_all('area'):
        company = {}
        company['name_curto'] = area.get('alt', '')
        href = area.get('href', '')
        slug_match = re.search(r'/trafego/pix/[^/]+/([^/]+)/bps', href)
        company['slug'] = slug_match.group(1) if slug_match else ''
        company['name_longo'] = area.get('title', '')
        company['coords'] = area.get('coords', '')
        companies.append(company)
    
    return companies

def main():
    base_url = 'https://ix.br'
    city_page_url = 'https://ix.br/trafego/pix/'
    
    city_info = get_city_info(city_page_url)
    
    os.makedirs('output', exist_ok=True)
    output_file = os.path.join('output', 'ix-br_slugs_data.csv')
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Sigla da Cidade', 'Nome da Cidade', 'UF do Estado', 'Nome curto Empresa', 'Slug', 'Nome longo Empresa', 'Coordenadas'])
        
        for city_code, city_uf in city_info:
            company_url = f'https://ix.br/trafego/pix/{city_code}'
            
            print(f"Processando: {company_url}")
            
            html_content = get_company_data(company_url)
            companies = extract_map_data(html_content)
            
            # Separar corretamente o nome da cidade e a UF
            city_parts = city_uf.split('/')
            if len(city_parts) >= 2:
                city_name = ' '.join(city_parts[:-1]).strip()
                uf = city_parts[-1].strip()
            else:
                city_name = city_uf
                uf = ''
            
            for company in companies:
                writer.writerow([
                    city_code,
                    city_name,
                    uf,
                    company['name_curto'],
                    company['slug'],
                    company['name_longo'],
                    company['coords']
                ])
            
            print(f"Dados processados e salvos para {city_name}")
            
            # Salva o CSV após processar cada cidade
            csvfile.flush()
            os.fsync(csvfile.fileno())
            
            time.sleep(1)  # Pausa de 1 segundo entre as requisições
    
    print(f"Todos os dados foram salvos em: {output_file}")

if __name__ == '__main__':
    main()
