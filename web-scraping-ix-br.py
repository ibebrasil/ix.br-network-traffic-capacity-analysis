import requests
from bs4 import BeautifulSoup, element
import csv
import re
import os
import time
from urllib.parse import urljoin

def get_city_urls_and_names(url):
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
    return [(option['value'], option.text.strip()) for option in options if option['value'].startswith('/adesao/')]

def create_slug(name):
    # Remove caracteres não alfanuméricos exceto hífens, e converte para minúsculas
    slug = re.sub(r'[^a-zA-Z0-9-]+', '', name.lower().replace(' ', ''))
    return slug

def extract_company_data(url, city_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    city_code = url.split('/')[-1]
    
    data = []
    state_uf = ""
    
    for item in soup.find_all(['b', 'br']):
        if isinstance(item, element.Tag) and item.name == 'b' and item.text.startswith('[') and item.text.endswith(']'):
            company = item.text.strip('[]')
            company = re.sub(r'^PIX\s*', '', company).strip()
            company_slug = create_slug(company)
            email_element = item.find_next(string=re.compile(r'\S+@\S+'))
            if email_element:
                email = email_element.strip()
                domain = email.split('@')[-1]
                
                # Procurar o UF do Estado após o e-mail
                next_element = email_element.find_next()
                while next_element:
                    if isinstance(next_element, element.NavigableString):
                        uf_match = re.search(r'\s-\s([A-Z]{2})', str(next_element))
                        if uf_match:
                            state_uf = uf_match.group(1)
                            break
                    elif isinstance(next_element, element.Tag) and next_element.name == 'b':
                        break
                    next_element = next_element.next_element
                
                data.append([city_code, city_name, state_uf, company, company_slug, email, domain])
    
    return data

def main():
    base_url = 'https://ix.br'
    city_page_url = 'https://ix.br/adesao/pix/'
    
    city_info = get_city_urls_and_names(city_page_url)
    
    all_data = []
    for city_path, city_name in city_info:
        url = urljoin(base_url, city_path)
        print(f"Processando: {url} - {city_name}")
        all_data.extend(extract_company_data(url, city_name))
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
