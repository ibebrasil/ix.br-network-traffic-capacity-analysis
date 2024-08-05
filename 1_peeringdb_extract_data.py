import requests
import csv
from dotenv import load_dotenv
from typing import List, Dict
import os
import time
from requests.exceptions import HTTPError
import pandas as pd
import json

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

MAX_RETRIES = 3
INITIAL_BACKOFF = 10  # segundos

# Configurações globais
API_BASE_URL = "https://www.peeringdb.com/api"
HEADERS = {
    "Authorization": "Api-Key " + secret_key,
    "Content-Type": "application/json"
}

# Arquivo de configuração para checkpoint
CONFIG_FILE = ".checkpoint.json"

def load_checkpoint():
    if os.path.exists(CONFIG_FILE) and os.path.getsize(CONFIG_FILE) > 0:
        with open(CONFIG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo de checkpoint. Criando um novo.")
    
    # Se o arquivo não existe, está vazio ou tem um erro de JSON, crie um novo
    default_checkpoint = {"step": 1, "progress": {}}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_checkpoint, f)
    return default_checkpoint

def save_checkpoint(step, progress):
    checkpoint = {"step": step, "progress": progress}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(checkpoint, f)

def fetch_with_retry(url: str, params: Dict) -> requests.Response:
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            return response
        except HTTPError as e:
            if e.response.status_code == 429 and attempt < MAX_RETRIES - 1:
                wait_time = INITIAL_BACKOFF * (2 ** attempt)
                print(f"Rate limit atingido. Aguardando {wait_time} segundos antes de tentar novamente...")
                time.sleep(wait_time)
            else:
                raise

def fetch_data(endpoint: str, params: Dict) -> List[Dict]:
    print("""Função para buscar dados da API com paginação.""")
    all_data = []

    # Se o endpoint for "/net" e houver "asn__in" nos parâmetros, dividimos em grupos menores
    if endpoint == "/net" and "asn__in" in params:
        asn_list = params["asn__in"].split(",")
        chunk_size = 250  # Reduzido para 50 para evitar atingir o limite de requisições
        for i in range(0, len(asn_list), chunk_size):
            chunk = asn_list[i:i + chunk_size]
            params_copy = params.copy()
            params_copy["asn__in"] = ",".join(chunk)
            all_data.extend(fetch_data_chunk(endpoint, params_copy))
        return all_data

    return fetch_data_chunk(endpoint, params)

def fetch_data_chunk(endpoint: str, params: Dict) -> List[Dict]:
    all_data = []
    skip = 0
    while True:
        params["depth"] = 1
        params["limit"] = 250
        params["skip"] = skip
        response = fetch_with_retry(f"{API_BASE_URL}{endpoint}", params)
        data = response.json()["data"]
        if not data:
            break
        all_data.extend(data)
        skip += 250
        print(f"Paginação: {skip}")
    return all_data

def save_csv(data: Dict, filename: str, mode='a'):
    print(f"""Adicionando dados ao arquivo CSV: {filename}""")
    file_exists = os.path.isfile(f"output/peeringdb_{filename}.csv")
    
    with open(f"output/peeringdb_{filename}.csv", mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def merge_data(data1: List[Dict], data2: List[Dict], key1: str, key2: str) -> List[Dict]:
    print("""Função para mesclar dois conjuntos de dados.""")
    merged = []
    data2_dict = {item[key2]: item for item in data2}
    for item in data1:
        merged_item = item.copy()
        if item[key1] in data2_dict:
            merged_item.update(data2_dict[item[key1]])
        merged.append(merged_item)
    return merged

def load_csv_data(filename: str) -> List[Dict]:
    print(f"Carregando dados do arquivo CSV: {filename}")
    file_path = f"output/peeringdb_{filename}.csv"
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado.")
        return []
    df = pd.read_csv(file_path)
    return df.to_dict('records')

def main():
    checkpoint = load_checkpoint()
    current_step = checkpoint["step"]
    progress = checkpoint["progress"]

    try:
        if current_step <= 1:
            print("# 1. Download all /ix with parameter 'country__in=BR'")
            ix_data = fetch_data("/ix", {"country__in": "BR"})
            for ix in ix_data:
                save_csv(ix, "ix_data")
            progress["ix_ids"] = [ix["id"] for ix in ix_data]
            current_step = 2
            save_checkpoint(current_step, progress)

        if current_step <= 2:
            print("# 2. Query /ixfac for each 'id' in ix_data")
            ixfac_data = fetch_data("/ixfac", {"ix_id__in": ",".join(map(str, progress["ix_ids"]))})
            for ixfac in ixfac_data:
                save_csv(ixfac, "ixfac_data")
            progress["fac_ids"] = list(set(ixfac["fac_id"] for ixfac in ixfac_data))
            current_step = 3
            save_checkpoint(current_step, progress)

        if current_step <= 3:
            print("# 3. Query /fac for each 'fac_id' in ixfac_data")
            fac_data = fetch_data("/fac", {"id__in": ",".join(map(str, progress["fac_ids"]))})
            for fac in fac_data:
                save_csv(fac, "fac_data")
            current_step = 4
            save_checkpoint(current_step, progress)

        if current_step <= 4:
            print("# 4. Merge IXFAC and FAC data")
            ixfac_data = load_csv_data("ixfac_data")
            fac_data = load_csv_data("fac_data")
            
            merged_ixfac_fac = merge_data(ixfac_data, fac_data, "fac_id", "id")
            
            # Clear existing CSV file before adding new data
            with open("output/peeringdb_merged_ixfac_fac_data.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=merged_ixfac_fac[0].keys())
                writer.writeheader()
                writer.writerows(merged_ixfac_fac)
            
            print(f"CSV file 'merged_ixfac_fac_data' generated with {len(merged_ixfac_fac)} records.")
            current_step = 5
            save_checkpoint(current_step, progress)

        if current_step <= 5:
            print("# 5. Query /netixlan for each 'id' in ix_data")
            netixlan_data = fetch_data("/netixlan", {"ix_id__in": ",".join(map(str, progress["ix_ids"]))})
            for netixlan in netixlan_data:
                save_csv(netixlan, "netixlan_data")
            progress["asns"] = list(set(netixlan["asn"] for netixlan in netixlan_data))
            current_step = 6
            save_checkpoint(current_step, progress)

        if current_step <= 6:
            print("# 6. Query /net for each 'asn' in netixlan_data")
            net_data = fetch_data("/net", {"asn__in": ",".join(map(str, progress["asns"]))})
            for net in net_data:
                save_csv(net, "net_data")
            current_step = 7
            save_checkpoint(current_step, progress)

        if current_step <= 7:
            print("# 7. Merge NETIXLAN and NET data")
            netixlan_data = load_csv_data("netixlan_data")
            net_data = load_csv_data("net_data")
            
            merged_netixlan_net = merge_data(netixlan_data, net_data, "asn", "asn")
            
            # Clear existing CSV file before adding new data
            with open("output/peeringdb_merged_netixlan_net_data.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=merged_netixlan_net[0].keys())
                writer.writeheader()
                writer.writerows(merged_netixlan_net)
            
            print(f"CSV file 'merged_netixlan_net_data' generated with {len(merged_netixlan_net)} records.")
            current_step = 8
            save_checkpoint(current_step, progress)

        print("Data extraction and merging completed. CSV files have been saved.")

    except Exception as e:
        print(f"An error occurred during execution at step {current_step}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
