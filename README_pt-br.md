# PeeringDB Data Extractor

[English Version](README_EN.md)

Este projeto consiste em um script Python para extrair e processar dados da API do PeeringDB, focando em informações sobre Internet Exchanges (IX) no Brasil e suas instalações associadas.

## Funcionalidades

- Extrai dados de IX no Brasil da API do PeeringDB
- Busca informações de IXFAC (IX Facility) para cada IX
- Obtém detalhes de FAC (Facility) para cada IXFAC
- Mescla os dados de IXFAC e FAC
- Salva os dados em formatos JSON e CSV

## Requisitos

- Python 3.8+
- Anaconda (recomendado para gerenciamento de ambiente)
- Chave de API do PeeringDB

## Configuração do Ambiente

Siga estas etapas para configurar o ambiente de desenvolvimento:

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/peeringdb-data-extractor.git
   cd peeringdb-data-extractor
   ```

2. Crie um ambiente Anaconda com Python 3.8:
   ```
   conda create -n peeringdb-env python=3.8
   ```

3. Ative o ambiente:
   ```
   conda activate peeringdb-env
   ```

4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

   Se encontrar conflitos de dependências, tente o seguinte:
   
   a. Primeiro, instale o NumPy:
      ```
      pip install "numpy>=1.23.5,<2.0.0"
      ```
   
   b. Em seguida, instale as demais dependências:
      ```
      pip install -r requirements.txt
      ```

   c. Se ainda enfrentar problemas, você pode tentar instalar as dependências ignorando os conflitos (use com cautela):
      ```
      pip install -r requirements.txt --ignore-installed
      ```

## Uso

1. Abra o arquivo `peeringdb_data_extractor.py` e substitua `<api-key>` pela sua chave de API do PeeringDB.

2. Execute o script:
   ```
   python peeringdb_data_extractor.py
   ```

3. Os arquivos de saída (JSON e CSV) serão gerados no diretório do script.

## Estrutura do Projeto

- `peeringdb_data_extractor.py`: Script principal
- `requirements.txt`: Lista de dependências do projeto
- `README.md`: Este arquivo

## Saída

O script gera os seguintes arquivos:

- `ix_data.json` e `ix_data.csv`: Dados dos IX no Brasil
- `merged_ixfac_fac_data.json` e `merged_ixfac_fac_data.csv`: Dados mesclados de IXFAC e FAC

## Resolução de Problemas

Se encontrar erros relacionados a conflitos de dependências, tente as seguintes soluções:

1. Atualize seu ambiente Anaconda:
   ```
   conda update --all
   ```

2. Se estiver usando um ambiente virtual, considere criar um novo ambiente e instalar as dependências nele.

3. Verifique se há conflitos com pacotes instalados globalmente. Você pode listar todos os pacotes instalados com:
   ```
   pip list
   ```
   
   E então desinstalar pacotes problemáticos que não são necessários para este projeto.

4. Se o problema persistir, considere reportar o problema criando uma issue no repositório do projeto.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue para discutir mudanças propostas ou envie um pull request.

## Licença

Este projeto está licenciado sob a [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html).

Esta licença garante que o software permaneça livre e de código aberto. Qualquer software derivado ou que utilize este código também deve ser distribuído sob os termos da GPL-3.0. Para mais detalhes, consulte o arquivo LICENSE no repositório ou visite o link da licença acima.
