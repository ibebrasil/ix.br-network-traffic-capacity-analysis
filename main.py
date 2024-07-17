import requests
import json
import csv
from typing import List, Dict
import os

# Configurações globais
API_BASE_URL = "https://www.peeringdb.com/api"
HEADERS = {
    "Authorization": "Api-Key gy6fQ2E3.Gwn03MgtNmoTSm3qOP2Jt54GcKfABTLn",
    "Content-Type": "application/json"
}

def fetch_data(endpoint: str, params: Dict) -> List[Dict]:
    """Função para buscar dados da API com paginação."""
    all_data = []
    skip = 0
    while True:
        params["depth"] = 1
        params["limit"] = 250
        params["skip"] = skip
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()["data"]
        if not data:
            break
        all_data.extend(data)
        skip += 250
    return all_data

def save_json(data: List[Dict], filename: str):
    """Função para salvar dados em formato JSON."""
    with open(f"{filename}.json", "w") as f:
        json.dump(data, f, indent=2)

def save_csv(data: List[Dict], filename: str):
    """Função para salvar dados em formato CSV."""
    if not data:
        return
    keys = data[0].keys()
    with open(f"{filename}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)

def merge_ixfac_and_fac_data(ixfac_data: List[Dict], fac_data: List[Dict]) -> List[Dict]:
    """Função para mesclar dados de IXFAC e FAC."""
    fac_dict = {fac['id']: fac for fac in fac_data}
    merged_data = []
    for ixfac in ixfac_data:
        fac = fac_dict.get(ixfac['fac_id'], {})
        merged_item = {**ixfac, **fac}
        merged_data.append(merged_item)
    return merged_data

def main():
    # 1. Baixar todos os /ix com o parâmetro 'country__in=BR'
    ix_data = fetch_data("/ix", {"country__in": "BR"})
    save_json(ix_data, "ix_data")
    save_csv(ix_data, "ix_data")

    # 2. Consultar /ixfac para cada 'id' em ix_data
    ix_ids = [ix["id"] for ix in ix_data]
    ixfac_data = fetch_data("/ixfac", {"ix_id__in": ",".join(map(str, ix_ids))})

    # 3. Consultar /fac para cada 'fac_id' em ixfac_data
    fac_ids = list(set(ixfac["fac_id"] for ixfac in ixfac_data))
    fac_data = fetch_data("/fac", {"id__in": ",".join(map(str, fac_ids))})

    # Mesclar dados de IXFAC e FAC
    merged_data = merge_ixfac_and_fac_data(ixfac_data, fac_data)

    # Salvar dados mesclados
    save_json(merged_data, "merged_ixfac_fac_data")
    save_csv(merged_data, "merged_ixfac_fac_data")

if __name__ == "__main__":
    main()
    print("Extração de dados concluída. Arquivos JSON e CSV foram salvos.")