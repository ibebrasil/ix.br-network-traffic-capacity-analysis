import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import openai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a chave da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def get_company_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text

def process_company_data(html_content):
    prompt = f"""
    Extraia as seguintes informações das empresas listadas no HTML abaixo:
    - Nome curto da empresa (geralmente em negrito, "::maker" pode anteceder, iniciado por PIX, e entre "[" e "]". Pode ser todo em caixa alta.)
    - Nome longoda empresa (geralmente em negrito, logo em seguida ao nome curto, não é todo em caixa alta.)
    - Nome do responsável (geralmente em negrito, antecede o e-mail)
    - E-mail do responsável
    - Domínio do e-mail (está contido no e-mail)

    Formato da resposta:
    Nome curto da empresa: <nome>
    Nome longo da empresa: <nome>
    Responsável: <nome>
    E-mail: <email>
    Domínio: <domínio>

    HTML:
    {html_content}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em extrair informações de HTML."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

def parse_gpt_response(response):
    companies = []
    current_company = {}
    for line in response.split('\n'):
        line = line.strip()
        if line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key, value = parts
                key = key.strip().lower()
                value = value.strip()
                if key == 'nome curto da empresa':
                    if current_company:
                        companies.append(current_company)
                    current_company = {'name_curto': value}
                elif key == 'nome longo da empresa':
                    current_company['name_longo'] = value
                elif key == 'responsável':
                    current_company['responsible'] = value
                elif key == 'e-mail':
                    current_company['email'] = value
                elif key == 'domínio':
                    current_company['domain'] = value
            else:
                print(f"Warning: Skipping malformed line: {line}")
    if current_company:
        companies.append(current_company)
    return companies

def main():
    base_url = 'https://ix.br'
    city_page_url = 'https://ix.br/trafego/pix/'
    
    city_info = get_city_info(city_page_url)
    
    os.makedirs('output', exist_ok=True)
    output_file = os.path.join('output', 'ix-br_entities_data.csv')
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Sigla da Cidade', 'Nome da Cidade', 'UF do Estado', 'Nome curto Empresa', 'Nome longo Empresa', 'Nome do Responsável', 'E-mail', 'Domínio'])
        
        for city_code, city_uf in city_info:
            company_url = f'https://ix.br/adesao/{city_code}'
            
            print(f"Processando: {company_url}")
            
            html_content = get_company_data(company_url)
            gpt_response = process_company_data(html_content)
            companies = parse_gpt_response(gpt_response)
            
            # Separar corretamente o nome da cidade e a UF
            city_name, uf = city_uf.rsplit('/', 1)
            
            for company in companies:
                writer.writerow([
                    city_code,
                    city_name,
                    uf,
                    company.get('name_curto', ''),
                    company.get('name_longo', ''),
                    company.get('responsible', ''),
                    company.get('email', ''),
                    company.get('domain', '')
                ])
            
            print(f"Dados processados e salvos para {city_name}")
            
            # Salva o CSV após processar cada cidade
            csvfile.flush()
            os.fsync(csvfile.fileno())
            
            time.sleep(1)  # Pausa de 1 segundo entre as requisições
    
    print(f"Todos os dados foram salvos em: {output_file}")

if __name__ == '__main__':
    main()
