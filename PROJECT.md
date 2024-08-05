# Project Flow Diagram

## Simplified Macro Algorithm

```mermaid
graph LR
    A[Start and Load Checkpoint] --> B[Fetch and Save IX Data]
    B --> C[Fetch and Save IXFAC Data]
    C --> D[Fetch and Save FAC Data]
    D --> E[Merge IXFAC and FAC Data]
    E --> F[Fetch and Save NETIXLAN Data]
    F --> G[Fetch and Save NET Data]
    G --> H[Merge NETIXLAN and NET Data]
    H --> I[End]
```

1. Start and Load Checkpoint
2. Fetch and Save IX Data (Internet Exchange Points in Brazil)
3. Fetch and Save IXFAC Data (IX Facility Data)
4. Fetch and Save FAC Data (Facility Data)
5. Merge IXFAC and FAC Data
6. Fetch and Save NETIXLAN Data (Network to IX Connection Data)
7. Fetch and Save NET Data (Network Information)
8. Merge NETIXLAN and NET Data
9. End

This simplified version provides a high-level overview of the main steps in the data collection and processing pipeline, omitting the repetitive checkpoint and progress update steps for clarity. The diagram above visually represents this simplified flow.

## Detailed Algorithm Diagram

```mermaid
graph TD
    A[Start] --> B[Load Checkpoint]
    B --> C{Check Current Step}
    
    C -->|Step 1| D1[Fetch IX Data]
    D1 --> E1[Save IX Data]
    E1 --> F1[Update Progress with IX IDs]
    F1 --> G1[Save Checkpoint]
    G1 --> C
    
    C -->|Step 2| D2[Fetch IXFAC Data using IX IDs]
    D2 --> E2[Save IXFAC Data]
    E2 --> F2[Update Progress with FAC IDs]
    F2 --> G2[Save Checkpoint]
    G2 --> C
    
    C -->|Step 3| D3[Fetch FAC Data using FAC IDs]
    D3 --> E3[Save FAC Data]
    E3 --> F3[Save Checkpoint]
    F3 --> C
    
    C -->|Step 4| D4[Load IXFAC and FAC Data]
    D4 --> E4[Merge IXFAC and FAC Data]
    E4 --> F4[Save Merged Data]
    F4 --> G4[Save Checkpoint]
    G4 --> C
    
    C -->|Step 5| D5[Fetch NETIXLAN Data using IX IDs]
    D5 --> E5[Save NETIXLAN Data]
    E5 --> F5[Update Progress with ASNs]
    F5 --> G5[Save Checkpoint]
    G5 --> C
    
    C -->|Step 6| D6[Fetch NET Data using ASNs]
    D6 --> E6[Save NET Data]
    E6 --> F6[Save Checkpoint]
    F6 --> C
    
    C -->|Step 7| D7[Load NETIXLAN and NET Data]
    D7 --> E7[Merge NETIXLAN and NET Data]
    E7 --> F7[Save Merged Data]
    F7 --> G7[Save Checkpoint]
    G7 --> C
    
    C -->|Step > 7| Z[End]
```

Este diagrama representa um fluxo mais detalhado do algoritmo no script, incluindo os passos onde os dados são obtidos de um checkpoint para fazer diversas chamadas em outro checkpoint e depois realizar a mesclagem dos dados.

Explicação do fluxo detalhado:

1. O processo começa carregando o checkpoint atual.
2. Em cada etapa, o script verifica o passo atual no checkpoint.
3. No Passo 1, os dados IX são buscados e salvos, e os IDs IX são armazenados no progresso do checkpoint.
4. No Passo 2, os dados IXFAC são buscados usando os IDs IX do checkpoint anterior, e os IDs FAC são armazenados no progresso.
5. No Passo 3, os dados FAC são buscados usando os IDs FAC do checkpoint anterior.
6. No Passo 4, os dados IXFAC e FAC são carregados dos arquivos CSV salvos e mesclados.
7. No Passo 5, os dados NETIXLAN são buscados usando os IDs IX, e os ASNs são armazenados no progresso.
8. No Passo 6, os dados NET são buscados usando os ASNs do checkpoint anterior.
9. No Passo 7, os dados NETIXLAN e NET são carregados dos arquivos CSV salvos e mesclados.

Após cada etapa, o checkpoint é atualizado com o progresso atual, permitindo que o script retome a execução a partir do último ponto concluído em caso de interrupção. Este fluxo detalhado mostra como os dados de checkpoints anteriores são utilizados para buscar informações adicionais e como os dados são mesclados em etapas subsequentes.

