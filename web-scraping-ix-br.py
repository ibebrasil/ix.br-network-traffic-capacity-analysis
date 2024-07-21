import requests
from bs4 import BeautifulSoup, element
import csv
import re
import os
import time
from urllib.parse import urljoin

def get_city_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    select = soup.find('select')
    
    if not select:
        print("Não foi possível encontrar o elemento select na página.")
        return []
    
    options = select.find_all('option')
    city_info = []
    for option in options:
        if 'Selecione' not in option.text and option.get('value'):
            value = option['value']
            city_uf = option.text.strip()
            city_code = value.split('/')[-1]
            city_info.append((city_code, city_uf))
    
    return city_info

def extract_company_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    
    for item in soup.find_all(['b', 'br']):
        if isinstance(item, element.Tag) and item.name == 'b' and item.text.startswith('[') and item.text.endswith(']'):
            company = item.text.strip('[]')
            company = re.sub(r'^PIX\s*', '', company).strip()
            email_element = item.find_next(string=re.compile(r'\S+@\S+'))
            email = email_element.strip() if email_element else ""
            domain = email.split('@')[-1] if email else ""
            
            data.append([company, email, domain])
    
    return data

def get_additional_company_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    company_data = {}
    map_tag = soup.find('map')
    if map_tag:
        for area in map_tag.find_all('area'):
            alt = area.get('alt', '')
            href = area.get('href', '')
            if href.startswith('/trafego/pix/'):
                slug = href.split('/')[-2]
                company_data[alt] = slug
    
    return company_data

def main():
    base_url = 'https://ix.br'
    city_page_url = 'https://ix.br/trafego/pix/'
    
    city_info = get_city_info(city_page_url)
    
    all_data = []
    for city_code, city_uf in city_info:
        company_url = f'https://ix.br/adesao/{city_code}'
        additional_data_url = f'https://ix.br/trafego/pix/{city_code}'
        
        print(f"Processando: {company_url}")
        company_data = extract_company_data(company_url)
        additional_data = get_additional_company_data(additional_data_url)
        
        # Separar corretamente o nome da cidade e a UF
        city_name, uf = city_uf.rsplit('/', 1)
        
        for company, email, domain in company_data:
            slug = ""
            for alt_name, company_slug in additional_data.items():
                if company.lower() in alt_name.lower() or alt_name.lower() in company.lower():
                    slug = company_slug
                    break
            
            all_data.append([city_code, city_name, uf, company, slug, email, domain])
        
        time.sleep(1)  # Pausa de 1 segundo entre as requisições
    
    os.makedirs('output', exist_ok=True)
    
    output_file = os.path.join('output', 'empresas_ix_br.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Sigla da Cidade', 'Nome da Cidade', 'UF do Estado', 'Empresa', 'Slug da Empresa', 'E-mail', 'Domínio'])
        writer.writerows(all_data)
    
    print(f"Dados salvos em: {output_file}")

if __name__ == '__main__':
    main()