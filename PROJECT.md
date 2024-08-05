# Project Flow Diagram

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
