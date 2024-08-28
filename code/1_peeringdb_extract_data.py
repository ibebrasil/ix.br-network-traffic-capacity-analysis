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
INITIAL_BACKOFF = 10  # seconds
MAX_IDS_PER_REQUEST = 100  # Limite máximo de IDs por requisição

# Global settings
API_BASE_URL = "https://www.peeringdb.com/api"
HEADERS = {
    "Authorization": "Api-Key " + secret_key,
    "Content-Type": "application/json"
}

# Configuration file for checkpoint
CONFIG_FILE = ".checkpoint.json"

def load_checkpoint():
    if os.path.exists(CONFIG_FILE) and os.path.getsize(CONFIG_FILE) > 0:
        with open(CONFIG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Error decoding checkpoint file. Creating a new one.")
    
    # If the file doesn't exist, is empty, or has a JSON error, create a new one
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
                print(f"Rate limit reached. Waiting {wait_time} seconds before trying again...")
                time.sleep(wait_time)
            else:
                raise

def fetch_data(endpoint: str, params: Dict) -> List[Dict]:
    print(f"Fetching data from {endpoint} with params: {params}")
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
        print(f"Pagination: {skip}")
    return all_data

def fetch_data_in_batches(endpoint: str, id_param: str, ids: List[int]) -> List[Dict]:
    all_data = []
    for i in range(0, len(ids), MAX_IDS_PER_REQUEST):
        batch_ids = ids[i:i + MAX_IDS_PER_REQUEST]
        params = {id_param: ",".join(map(str, batch_ids))}
        all_data.extend(fetch_data(endpoint, params))
    return all_data

def save_csv(data: List[Dict], filename: str):
    print(f"Saving data to CSV file: {filename}")
    if not data:
        print(f"No data to save for {filename}")
        return
    with open(f"output/peeringdb_{filename}.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def main():
    checkpoint = load_checkpoint()
    current_step = checkpoint["step"]
    progress = checkpoint["progress"]

    try:
        if current_step <= 1:
            print("# 1. Consultar IXs do Brasil")
            ix_data = fetch_data("/ix", {"country": "BR"})
            save_csv(ix_data, "ix_data")
            progress["ix_ids"] = [ix["id"] for ix in ix_data]
            current_step = 2
            save_checkpoint(current_step, progress)

        if current_step <= 2:
            print("# 2. Consultar IXLANs associadas aos IXs do Brasil")
            ixlan_data = fetch_data_in_batches("/ixlan", "ix_id__in", progress["ix_ids"])
            save_csv(ixlan_data, "ixlan_data")
            progress["ixlan_ids"] = [ixlan["id"] for ixlan in ixlan_data]
            current_step = 3
            save_checkpoint(current_step, progress)

        if current_step <= 3:
            print("# 3. Consultar NETIXLANs associadas às IXLANs")
            netixlan_data = fetch_data_in_batches("/netixlan", "ixlan_id__in", progress["ixlan_ids"])
            save_csv(netixlan_data, "netixlan_data")
            current_step = 4
            save_checkpoint(current_step, progress)

        if current_step <= 4:
            print("# 4. Consultar FACs do Brasil")
            fac_data = fetch_data("/fac", {"country": "BR"})
            save_csv(fac_data, "fac_data")
            progress["fac_ids"] = [fac["id"] for fac in fac_data]
            current_step = 5
            save_checkpoint(current_step, progress)

        if current_step <= 5:
            print("# 5. Consultar IXFACs associados às FACs do Brasil")
            ixfac_data = fetch_data_in_batches("/ixfac", "fac_id__in", progress["fac_ids"])
            save_csv(ixfac_data, "ixfac_data")
            current_step = 6
            save_checkpoint(current_step, progress)

        if current_step <= 6:
            print("# 6. Consultar NETs associadas aos IXs e FACs do Brasil")
            net_data = fetch_data_in_batches("/net", "ix_id__in", progress["ix_ids"])
            net_data.extend(fetch_data_in_batches("/net", "fac_id__in", progress["fac_ids"]))
            save_csv(net_data, "net_data")
            progress["net_ids"] = list(set(net["id"] for net in net_data))
            current_step = 7
            save_checkpoint(current_step, progress)

        if current_step <= 7:
            print("# 7. Consultar POCs associados às NETs")
            poc_data = fetch_data_in_batches("/poc", "net_id__in", progress["net_ids"])
            save_csv(poc_data, "poc_data")
            current_step = 8
            save_checkpoint(current_step, progress)

        print("# 8. Construir tabela unificada")
        build_unified_table()

        print("Data extraction and unification completed. CSV files have been saved.")

    except Exception as e:
        print(f"An error occurred during execution at step {current_step}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Sempre construir a tabela unificada, independentemente de erros anteriores
        print("# Construindo tabela unificada final")
        build_unified_table()

def build_unified_table():
    ix_df = pd.read_csv("output/peeringdb_ix_data.csv")
    ixlan_df = pd.read_csv("output/peeringdb_ixlan_data.csv")
    netixlan_df = pd.read_csv("output/peeringdb_netixlan_data.csv")
    fac_df = pd.read_csv("output/peeringdb_fac_data.csv")
    ixfac_df = pd.read_csv("output/peeringdb_ixfac_data.csv")
    net_df = pd.read_csv("output/peeringdb_net_data.csv")

    # Selecionar colunas relevantes
    ix_df = ix_df[['id', 'name', 'city', 'country', 'org_id']]
    ixlan_df = ixlan_df[['id', 'ix_id', 'name']]
    netixlan_df = netixlan_df[['id', 'net_id', 'ix_id', 'ixlan_id', 'asn', 'ipaddr4', 'ipaddr6', 'speed']]
    fac_df = fac_df[['id', 'name', 'city', 'country', 'org_id']]
    ixfac_df = ixfac_df[['id', 'ix_id', 'fac_id']]
    net_df = net_df[['id', 'name', 'asn', 'info_type', 'policy_general']]

    # Mesclar dataframes
    merged_df = netixlan_df.merge(ixlan_df, left_on='ixlan_id', right_on='id', suffixes=('', '_ixlan'))
    merged_df = merged_df.merge(ix_df, left_on='ix_id', right_on='id', suffixes=('', '_ix'))
    merged_df = merged_df.merge(ixfac_df, on='ix_id', suffixes=('', '_ixfac'))
    merged_df = merged_df.merge(fac_df, left_on='fac_id', right_on='id', suffixes=('', '_fac'))
    merged_df = merged_df.merge(net_df, left_on='net_id', right_on='id', suffixes=('', '_net'))

    # Renomear colunas para evitar ambiguidades e remover duplicatas
    column_mapping = {
        'id': 'netixlan_id',
        'id_ixlan': 'ixlan_id',
        'id_ix': 'ix_id',
        'id_ixfac': 'ixfac_id',
        'id_fac': 'fac_id',
        'id_net': 'net_id',
        'name': 'netixlan_name',
        'name_ixlan': 'ixlan_name',
        'name_ix': 'ix_name',
        'name_fac': 'fac_name',
        'name_net': 'net_name',
        'city': 'ix_city',
        'city_fac': 'fac_city',
        'country': 'ix_country',
        'country_fac': 'fac_country',
        'org_id': 'ix_org_id',
        'org_id_fac': 'fac_org_id',
        'asn': 'net_asn',
        'asn_net': 'net_asn'
    }
    merged_df = merged_df.rename(columns=column_mapping)

    # Remover colunas duplicadas
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

    # Remover duplicatas de linhas
    merged_df = merged_df.drop_duplicates()

    # Salvar tabela unificada
    merged_df.to_csv("output/peeringdb_unified_data.csv", index=False)
    print("Tabela unificada salva como 'output/peeringdb_unified_data.csv'")

if __name__ == "__main__":
    main()
