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
graph LR
    A[Start] --> B[Load Checkpoint]
    B --> C{Check Current Step}
    
    subgraph Step1[Step 1]
    direction LR
    D1[Fetch IX Data] --> E1[Save IX Data] --> F1[Update Progress with IX IDs] --> G1[Save Checkpoint]
    end
    
    subgraph Step2[Step 2]
    direction LR
    D2[Fetch IXFAC Data using IX IDs] --> E2[Save IXFAC Data] --> F2[Update Progress with FAC IDs] --> G2[Save Checkpoint]
    end
    
    subgraph Step3[Step 3]
    direction LR
    D3[Fetch FAC Data using FAC IDs] --> E3[Save FAC Data] --> F3[Save Checkpoint]
    end
    
    subgraph Step4[Step 4]
    direction LR
    D4[Load IXFAC and FAC Data] --> E4[Merge IXFAC and FAC Data] --> F4[Save Merged Data] --> G4[Save Checkpoint]
    end
    
    subgraph Step5[Step 5]
    direction LR
    D5[Fetch NETIXLAN Data using IX IDs] --> E5[Save NETIXLAN Data] --> F5[Update Progress with ASNs] --> G5[Save Checkpoint]
    end
    
    subgraph Step6[Step 6]
    direction LR
    D6[Fetch NET Data using ASNs] --> E6[Save NET Data] --> F6[Save Checkpoint]
    end
    
    subgraph Step7[Step 7]
    direction LR
    D7[Load NETIXLAN and NET Data] --> E7[Merge NETIXLAN and NET Data] --> F7[Save Merged Data] --> G7[Save Checkpoint]
    end
    
    C -->|Step 1| Step1
    C -->|Step 2| Step2
    C -->|Step 3| Step3
    C -->|Step 4| Step4
    C -->|Step 5| Step5
    C -->|Step 6| Step6
    C -->|Step 7| Step7
    
    Step1 --> C
    Step2 --> C
    Step3 --> C
    Step4 --> C
    Step5 --> C
    Step6 --> C
    Step7 --> C
    
    C -->|Step > 7| Z[End]
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

