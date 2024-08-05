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

## Diagram

```mermaid
graph LR
    A[Start] --> B[Load Checkpoint]
    B --> C{Check Current Step}
    
    C -->|Step 1| D1[Fetch IX Data]
    D1 --> E1[Save IX Data]
    E1 --> F1[Update Progress]
    F1 --> G1[Save Checkpoint]
    G1 --> C
    
    C -->|Step 2| D2[Fetch IXFAC Data]
    D2 --> E2[Save IXFAC Data]
    E2 --> F2[Update Progress]
    F2 --> G2[Save Checkpoint]
    G2 --> C
    
    C -->|Step 3| D3[Fetch FAC Data]
    D3 --> E3[Save FAC Data]
    E3 --> F3[Save Checkpoint]
    F3 --> C
    
    C -->|Step 4| D4[Merge IXFAC and FAC Data]
    D4 --> E4[Save Merged Data]
    E4 --> F4[Save Checkpoint]
    F4 --> C
    
    C -->|Step 5| D5[Fetch NETIXLAN Data]
    D5 --> E5[Save NETIXLAN Data]
    E5 --> F5[Update Progress]
    F5 --> G5[Save Checkpoint]
    G5 --> C
    
    C -->|Step 6| D6[Fetch NET Data]
    D6 --> E6[Save NET Data]
    E6 --> F6[Save Checkpoint]
    F6 --> C
    
    C -->|Step 7| D7[Merge NETIXLAN and NET Data]
    D7 --> E7[Save Merged Data]
    E7 --> F7[Save Checkpoint]
    F7 --> C
    
    C -->|Step > 7| Z[End]
```

This diagram represents the macro flow of the algorithm in the script. It shows the step-by-step process, including checkpointing, data fetching, saving, and merging operations. The steps are now arranged vertically and in ascending order from left to right.

