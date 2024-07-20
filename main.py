import requests
import json
import csv
from dotenv import load_dotenv
from typing import List, Dict
import os

load_dotenv()

secret_key = os.getenv('SECRET_KEY')

# Configurações globais
API_BASE_URL = "https://www.peeringdb.com/api"
HEADERS = {
    "Authorization": "Api-Key " + secret_key,
    "Content-Type": "application/json"
}

def fetch_data(endpoint: str, params: Dict) -> List[Dict]:
    print("""Função para buscar dados da API com paginação.""")
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
        print(f"Paginação: {skip}")
    return all_data

def save_json(data: List[Dict], filename: str):
    print("""Função para salvar dados em formato JSON.""")
    with open(f"output/{filename}.json", "w") as f:
        json.dump(data, f, indent=2)

def save_csv(data: List[Dict], filename: str):
    print("""Função para salvar dados em formato CSV.""")
    if not data:
        return
    keys = data[0].keys()
    with open(f"output/{filename}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)

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

def main():
    print("# 1. Baixar todos os /ix com o parâmetro 'country__in=BR'")
    ix_data = fetch_data("/ix", {"country__in": "BR"})
    save_json(ix_data, "ix_data")
    save_csv(ix_data, "ix_data")

    print("# 2. Consultar /ixfac para cada 'id' em ix_data")
    ix_ids = [ix["id"] for ix in ix_data]
    ixfac_data = fetch_data("/ixfac", {"ix_id__in": ",".join(map(str, ix_ids))})

    print("# 3. Consultar /fac para cada 'fac_id' em ixfac_data")
    fac_ids = list(set(ixfac["fac_id"] for ixfac in ixfac_data))
    fac_data = fetch_data("/fac", {"id__in": ",".join(map(str, fac_ids))})

    print("# Mesclar dados de IXFAC e FAC")
    merged_ixfac_fac = merge_data(ixfac_data, fac_data, "fac_id", "id")
    save_json(merged_ixfac_fac, "merged_ixfac_fac_data")
    save_csv(merged_ixfac_fac, "merged_ixfac_fac_data")

    print("# 4. Consultar /netixlan para cada 'id' em ix_data")
    netixlan_data = fetch_data("/netixlan", {"ix_id__in": ",".join(map(str, ix_ids))})
    save_json(netixlan_data, "netixlan_data")
    save_csv(netixlan_data, "netixlan_data")

    print("# 5. Consultar /net para cada 'asn' em netixlan_data")
    asns = list(set(netixlan["asn"] for netixlan in netixlan_data))
    net_data = fetch_data("/net", {"asn__in": ",".join(map(str, asns))})
    save_json(net_data, "net_data")
    save_csv(net_data, "net_data")

    print("# Mesclar dados de NETIXLAN e NET")
    merged_netixlan_net = merge_data(netixlan_data, net_data, "asn", "asn")
    save_json(merged_netixlan_net, "merged_netixlan_net_data")
    save_csv(merged_netixlan_net, "merged_netixlan_net_data")

if __name__ == "__main__":
    main()
    print("Extração de dados concluída. Arquivos JSON e CSV foram salvos.")
