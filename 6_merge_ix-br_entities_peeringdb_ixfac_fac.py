import pandas as pd

# Leitura dos arquivos CSV
peeringdb_df = pd.read_csv('output/peeringdb_merged_ixfac_fac_data.csv')
ixbr_df = pd.read_csv('output/ix-br_entities_data.csv')

# Função para extrair o domínio do URL
def extract_domain(url):
    if pd.isna(url) or '//' not in url:
        return ''
    domain = url.split('//')[1].split('/')[0]
    return domain

# Criando uma nova coluna com o domínio extraído
peeringdb_df['dominio_extraido'] = peeringdb_df['website'].apply(extract_domain)

# Convertendo colunas de domínio para minúsculas para garantir correspondência correta
peeringdb_df['dominio_extraido'] = peeringdb_df['dominio_extraido'].str.lower()
ixbr_df['Domínio'] = ixbr_df['Domínio'].str.lower()

# Fazer o merge das tabelas com base na coluna de domínio
merged_df = pd.merge(peeringdb_df, ixbr_df, left_on='dominio_extraido', right_on='Domínio', how='inner')

# Salvar o resultado em um novo CSV
merged_df.to_csv('output/merged_data.csv', index=False)

print("Merge concluído! O arquivo 'merged_data.csv' foi gerado.")
