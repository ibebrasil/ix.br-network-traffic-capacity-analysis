import pandas as pd
from rapidfuzz import fuzz, process

# Carregar os dados dos arquivos CSV
entities_df = pd.read_csv('output/ix-br_entities_data.csv')
slugs_df = pd.read_csv('output/ix-br_slugs_data_processed.csv')

# Iniciar um dataframe para armazenar os resultados do merge
merged_results = []

# Iterar sobre o dataframe de empresas (entities_df)
for _, entity_row in entities_df.iterrows():
    entity_city = entity_row['Sigla da Cidade']
    entity_name = entity_row['Nome curto Empresa']
    
    # Filtrar os slugs que pertencem à mesma cidade
    city_slugs = slugs_df[slugs_df['Sigla da Cidade'] == entity_city]
    
    best_match = None
    highest_score = 0
    
    # Iterar sobre os slugs filtrados para encontrar a melhor correspondência usando fuzz.partial_ratio
    for _, slug_row in city_slugs.iterrows():
        slug_name = slug_row['Slug']
        
        # Usar fuzz.partial_ratio para permitir correspondências parciais
        score = fuzz.partial_ratio(slug_name.lower(), entity_name.lower())
        
        # Verificar se essa correspondência é a melhor até agora
        if score > highest_score:
            highest_score = score
            best_match = slug_row
    
    # Se encontrou um bom match, adiciona ao resultado
    if best_match is not None:
        merged_result = {**best_match.to_dict(), **entity_row.to_dict(), 'Score': highest_score}
    else:
        # Se não encontrou um match, adiciona a empresa com campos de slug vazios
        empty_slug = {col: None for col in slugs_df.columns}
        merged_result = {**empty_slug, **entity_row.to_dict(), 'Score': None}
    
    # Garantir que os campos de empresa não fiquem vazios
    for field in ['Nome curto Empresa', 'Nome longo Empresa']:
        if pd.isna(merged_result[field]) or merged_result[field] == "":
            merged_result[field] = entity_row[field]
    
    merged_results.append(merged_result)

# Iterar sobre os slugs que não foram utilizados e adicioná-los ao final, sem empresa associada
used_slugs = set(row['Slug'] for row in merged_results if row['Slug'])
unused_slugs = slugs_df[~slugs_df['Slug'].isin(used_slugs)]

for _, slug_row in unused_slugs.iterrows():
    empty_entity = {col: None for col in entities_df.columns}
    merged_result = {**slug_row.to_dict(), **empty_entity, 'Score': None}
    merged_results.append(merged_result)

# Convertendo os resultados em um DataFrame
merged_df = pd.DataFrame(merged_results)

# Salvar o DataFrame resultante em um arquivo CSV
merged_df.to_csv('output/merged_ix_br_data.csv', index=False)

print("Merge completed and saved as 'merged_ix_br_data.csv'.")
