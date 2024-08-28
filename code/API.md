# Diagrama de Entidade Relacionamento da API do PeeringDB

```mermaid
erDiagram
    NET ||--o{ NETFAC : "tem"
    NET ||--o{ NETIXLAN : "tem"
    NET ||--o{ POC : "tem"
    FAC ||--o{ NETFAC : "tem"
    IX ||--o{ IXLAN : "tem"
    IX ||--o{ IXFAC : "tem"
    IXLAN ||--o{ NETIXLAN : "tem"
    FAC ||--o{ IXFAC : "tem"

    NET {
        %% Identificação
        int id PK "Identificador único"
        string name "Nome da rede"
        string aka "Também conhecido como"
        int asn "Número do Sistema Autônomo"
        
        %% Informações gerais
        string website "Site da rede"
        string looking_glass "URL do Looking Glass"
        string route_server "URL do Route Server"
        string irr_as_set "IRR AS-SET"
        
        %% Informações técnicas
        string info_type "Tipo de rede"
        string info_prefixes4 "Prefixos IPv4"
        string info_prefixes6 "Prefixos IPv6"
        string info_traffic "Volume de tráfego"
        string info_scope "Escopo geográfico"
        string info_ratio "Razão de tráfego"
        string info_unicast "Suporte a unicast"
        string info_multicast "Suporte a multicast"
        
        %% Políticas
        string policy_url "URL da política"
        string policy_general "Política geral"
        string policy_locations "Política de localização"
        string policy_ratio "Política de razão"
        string policy_contracts "Política de contratos"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    FAC {
        %% Identificação
        int id PK "Identificador único"
        string name "Nome da instalação"
        
        %% Informações gerais
        string website "Site da instalação"
        string clli "Código CLLI"
        string rencode "Código REN"
        string npanxx "Código NPANXX"
        string notes "Notas"
        
        %% Organização
        string org_id FK "ID da organização"
        string org_name "Nome da organização"
        
        %% Localização
        float latitude "Latitude"
        float longitude "Longitude"
        string address1 "Endereço (linha 1)"
        string address2 "Endereço (linha 2)"
        string city "Cidade"
        string country "País"
        string state "Estado"
        string zipcode "CEP"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    IX {
        %% Identificação
        int id PK "Identificador único"
        string name "Nome do IX"
        string name_long "Nome completo do IX"
        
        %% Localização
        string city "Cidade"
        string country "País"
        
        %% Informações gerais
        string notes "Notas"
        string org_id FK "ID da organização"
        string org_name "Nome da organização"
        
        %% Contatos
        string policy_email "Email de política"
        string policy_phone "Telefone de política"
        string tech_email "Email técnico"
        string tech_phone "Telefone técnico"
        
        %% URLs
        string website "Site do IX"
        string url_stats "URL de estatísticas"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    IXLAN {
        %% Identificação
        int id PK "Identificador único"
        int ix_id FK "ID do IX associado"
        string name "Nome da LAN"
        
        %% Informações técnicas
        string descr "Descrição"
        int mtu "MTU"
        int dot1q_support "Suporte a 802.1Q"
        int rs_asn "ASN do Route Server"
        string arp_sponge "ARP Sponge"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    NETFAC {
        %% Identificação
        int id PK "Identificador único"
        int net_id FK "ID da rede"
        int fac_id FK "ID da instalação"
        
        %% Informações técnicas
        string local_asn "ASN local"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    NETIXLAN {
        %% Identificação
        int id PK "Identificador único"
        int net_id FK "ID da rede"
        int ix_id FK "ID do IX"
        int ixlan_id FK "ID da LAN do IX"
        string name "Nome"
        
        %% Informações técnicas
        int asn "ASN"
        string ipaddr4 "Endereço IPv4"
        string ipaddr6 "Endereço IPv6"
        int speed "Velocidade"
        string operational "Status operacional"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    POC {
        %% Identificação
        int id PK "Identificador único"
        int net_id FK "ID da rede associada"
        
        %% Informações de contato
        string role "Função"
        string visible "Visibilidade"
        string name "Nome"
        string phone "Telefone"
        string email "Email"
        string url "URL"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }

    IXFAC {
        %% Identificação
        int id PK "Identificador único"
        int ix_id FK "ID do IX"
        int fac_id FK "ID da instalação"
        
        %% Metadados
        date created "Data de criação"
        date updated "Data de atualização"
        string status "Status do registro"
    }
```

Este diagrama representa as principais entidades e seus relacionamentos na API do PeeringDB. Cada entidade inclui seus atributos mais relevantes, agrupados por categoria e com descrições breves. Os endpoints principais são:

1. /net (Redes)
2. /fac (Instalações)
3. /ix (Pontos de Troca de Internet)
4. /ixlan (LANs de IX)
5. /netfac (Relação entre Redes e Instalações)
6. /netixlan (Relação entre Redes e LANs de IX)
7. /poc (Pontos de Contato)
8. /ixfac (Relação entre IXs e Instalações)

Cada um desses endpoints permite operações CRUD (Create, Read, Update, Delete) através de requisições HTTP apropriadas.

Legenda:
- PK: Chave Primária (Primary Key)
- FK: Chave Estrangeira (Foreign Key)

## Diagrama de Relações entre Entidades do PeeringDB

A seguir, apresentamos um diagrama Mermaid que representa as relações entre as principais entidades do PeeringDB:

```mermaid
graph TD
    NET[Redes NET]
    FAC[Instalações FAC]
    IX[IX Pontos de Troca de Internet]
    
    subgraph NET
        NETFAC1[NETFAC]
        NETIXLAN1[NETIXLAN]
        POC[POC]
    end
    
    subgraph FAC
        NETFAC2[NETFAC]
        IXFAC1[IXFAC]
    end
    
    subgraph IX
        NETIXLAN2[NETIXLAN]
        IXLAN[IXLAN]
        IXFAC2[IXFAC]
    end
    
    NET --- FAC
    NET --- IX
    FAC --- IX
    
    NETFAC1 -.-> NETFAC2
    NETIXLAN1 -.-> NETIXLAN2
    IXFAC1 -.-> IXFAC2
```

Este diagrama Mermaid mostra as seguintes relações:

1. NET (Redes) contém:
   - NETFAC: Relação entre Redes e Instalações
   - NETIXLAN: Relação entre Redes e LANs de IX
   - POC: Pontos de Contato das Redes

2. FAC (Instalações) contém:
   - NETFAC: Relação entre Redes e Instalações
   - IXFAC: Relação entre IXs e Instalações

3. IX (Pontos de Troca de Internet) contém:
   - IXLAN: LANs de IX
   - IXFAC: Relação entre IXs e Instalações
   - NETIXLAN: Relação entre Redes e LANs de IX

4. A interseção entre NET e FAC é representada por NETFAC
5. A interseção entre FAC e IX é representada por IXFAC
6. A interseção entre NET e IX é representada por NETIXLAN, que está ligada a IXLAN

Esta representação ajuda a visualizar como as diferentes entidades do PeeringDB se relacionam entre si, destacando as entidades de junção (NETFAC, NETIXLAN, IXFAC) que conectam as entidades principais (NET, FAC, IX).

## Fluxo Ideal de Consultas para Dados do Brasil

Para obter uma única tabela com todos os dados de IX, FAC e NET do Brasil (BR), siga este fluxo de consultas:

1. Consultar IXs do Brasil:
   ```
   GET /ix?country=BR
   ```
   Atributos relevantes: id, name, city, country, org_id

2. Para cada IX, consultar IXLANs associadas:
   ```
   GET /ixlan?ix_id={ix_id}
   ```
   Atributos relevantes: id, ix_id, name

3. Para cada IXLAN, consultar NETIXLANs associadas:
   ```
   GET /netixlan?ixlan_id={ixlan_id}
   ```
   Atributos relevantes: id, net_id, ix_id, ixlan_id, asn, ipaddr4, ipaddr6, speed

4. Consultar FACs do Brasil:
   ```
   GET /fac?country=BR
   ```
   Atributos relevantes: id, name, city, country, org_id

5. Para cada FAC, consultar IXFACs associados:
   ```
   GET /ixfac?fac_id={fac_id}
   ```
   Atributos relevantes: id, ix_id, fac_id

6. Consultar NETs associadas aos IXs e FACs do Brasil:
   ```
   GET /net?ix_id={ix_id1},{ix_id2},...&fac_id={fac_id1},{fac_id2},...
   ```
   Atributos relevantes: id, name, asn, info_type, policy_general

7. Para cada NET, consultar POCs associados:
   ```
   GET /poc?net_id={net_id}
   ```
   Atributos relevantes: id, net_id, role, name, email, phone

Com essas consultas, você pode construir uma tabela unificada com as seguintes colunas:

1. IX: id, name, city, country, org_id
2. IXLAN: id, ix_id, name
3. NETIXLAN: id, net_id, ix_id, ixlan_id, asn, ipaddr4, ipaddr6, speed
4. FAC: id, name, city, country, org_id
5. IXFAC: id, ix_id, fac_id
6. NET: id, name, asn, info_type, policy_general
7. POC: id, net_id, role, name, email, phone

Esta tabela unificada fornecerá uma visão abrangente da infraestrutura de interconexão no Brasil, incluindo pontos de troca de internet, instalações, redes participantes e seus pontos de contato.

## Diagrama do Fluxo de Consultas para Dados do Brasil

O seguinte diagrama Mermaid ilustra o fluxo de consultas para obter dados do Brasil:

```mermaid
graph TD
    A[Início] --> B[Consultar IXs do Brasil]
    B --> C[Para cada IX, consultar IXLANs]
    C --> D[Para cada IXLAN, consultar NETIXLANs]
    B --> E[Consultar FACs do Brasil]
    E --> F[Para cada FAC, consultar IXFACs]
    B & E --> G[Consultar NETs associadas aos IXs e FACs]
    G --> H[Para cada NET, consultar POCs]
    H --> I[Construir tabela unificada]
    I --> J[Fim]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
```

Este diagrama mostra a sequência de consultas necessárias para obter todos os dados relevantes do Brasil, começando com os IXs e FACs, e então obtendo as informações relacionadas de IXLANs, NETIXLANs, IXFACs, NETs e POCs. O processo termina com a construção da tabela unificada que contém todas as informações coletadas.
