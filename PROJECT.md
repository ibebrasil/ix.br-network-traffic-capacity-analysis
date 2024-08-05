# Project Flow Diagram

## Simplified Macro Algorithm

```mermaid
graph TD
    A[Step 1: Start and Load Checkpoint]
    B[Step 2: Fetch and Save IX Data]
    C[Step 3: Fetch and Save IXFAC Data]
    D[Step 4: Fetch and Save FAC Data]
    E[Step 5: Merge IXFAC and FAC Data]
    F[Step 6: Fetch and Save NETIXLAN Data]
    G[Step 7: Fetch and Save NET Data]
    H[Step 8: Merge NETIXLAN and NET Data]
    I[Step 9: End]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
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
    A[Start]
    B[Load Checkpoint]
    C{Check Current Step}
    
    D1[Step 1: Fetch IX Data]
    E1[Save IX Data]
    F1[Update Progress with IX IDs]
    G1[Save Checkpoint]
    
    D2[Step 2: Fetch IXFAC Data using IX IDs]
    E2[Save IXFAC Data]
    F2[Update Progress with FAC IDs]
    G2[Save Checkpoint]
    
    D3[Step 3: Fetch FAC Data using FAC IDs]
    E3[Save FAC Data]
    F3[Save Checkpoint]
    
    D4[Step 4: Load IXFAC and FAC Data]
    E4[Merge IXFAC and FAC Data]
    F4[Save Merged Data]
    G4[Save Checkpoint]
    
    D5[Step 5: Fetch NETIXLAN Data using IX IDs]
    E5[Save NETIXLAN Data]
    F5[Update Progress with ASNs]
    G5[Save Checkpoint]
    
    D6[Step 6: Fetch NET Data using ASNs]
    E6[Save NET Data]
    F6[Save Checkpoint]
    
    D7[Step 7: Load NETIXLAN and NET Data]
    E7[Merge NETIXLAN and NET Data]
    F7[Save Merged Data]
    G7[Save Checkpoint]
    
    Z[End]

    A --> B
    B --> C
    
    C -->|Step 1| D1
    D1 --> E1
    E1 --> F1
    F1 --> G1
    G1 --> C
    
    C -->|Step 2| D2
    D2 --> E2
    E2 --> F2
    F2 --> G2
    G2 --> C
    
    C -->|Step 3| D3
    D3 --> E3
    E3 --> F3
    F3 --> C
    
    C -->|Step 4| D4
    D4 --> E4
    E4 --> F4
    F4 --> G4
    G4 --> C
    
    C -->|Step 5| D5
    D5 --> E5
    E5 --> F5
    F5 --> G5
    G5 --> C
    
    C -->|Step 6| D6
    D6 --> E6
    E6 --> F6
    F6 --> C
    
    C -->|Step 7| D7
    D7 --> E7
    E7 --> F7
    F7 --> G7
    G7 --> C
    
    C -->|Step > 7| Z
```

This diagram represents a more detailed flow of the algorithm in the script, including the steps where data is retrieved from one checkpoint to make multiple calls in another checkpoint and then merge the data.

Explanation of the detailed flow:

1. The process begins by loading the current checkpoint.
2. At each stage, the script checks the current step in the checkpoint.
3. In Step 1, IX data is fetched and saved, and IX IDs are stored in the checkpoint progress.
4. In Step 2, IXFAC data is fetched using IX IDs from the previous checkpoint, and FAC IDs are stored in the progress.
5. In Step 3, FAC data is fetched using FAC IDs from the previous checkpoint.
6. In Step 4, IXFAC and FAC data are loaded from saved CSV files and merged.
7. In Step 5, NETIXLAN data is fetched using IX IDs, and ASNs are stored in the progress.
8. In Step 6, NET data is fetched using ASNs from the previous checkpoint.
9. In Step 7, NETIXLAN and NET data are loaded from saved CSV files and merged.

After each step, the checkpoint is updated with the current progress, allowing the script to resume execution from the last completed point in case of interruption. This detailed flow shows how data from previous checkpoints is used to fetch additional information and how data is merged in subsequent steps.

