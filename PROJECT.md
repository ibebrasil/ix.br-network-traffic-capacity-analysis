# Project Flow Diagram

```mermaid
graph TD
    A[Start] --> B[Load Checkpoint]
    B --> C{Check Current Step}
    
    C -->|Step 1| D[Fetch IX Data]
    D --> E[Save IX Data]
    E --> F[Update Progress]
    F --> G[Save Checkpoint]
    G --> C
    
    C -->|Step 2| H[Fetch IXFAC Data]
    H --> I[Save IXFAC Data]
    I --> J[Update Progress]
    J --> K[Save Checkpoint]
    K --> C
    
    C -->|Step 3| L[Fetch FAC Data]
    L --> M[Save FAC Data]
    M --> N[Save Checkpoint]
    N --> C
    
    C -->|Step 4| O[Merge IXFAC and FAC Data]
    O --> P[Save Merged Data]
    P --> Q[Save Checkpoint]
    Q --> C
    
    C -->|Step 5| R[Fetch NETIXLAN Data]
    R --> S[Save NETIXLAN Data]
    S --> T[Update Progress]
    T --> U[Save Checkpoint]
    U --> C
    
    C -->|Step 6| V[Fetch NET Data]
    V --> W[Save NET Data]
    W --> X[Save Checkpoint]
    X --> C
    
    C -->|Step 7| Y[Merge NETIXLAN and NET Data]
    Y --> Z[Save Merged Data]
    Z --> AA[Save Checkpoint]
    AA --> C
    
    C -->|Step > 7| AB[End]
```

This diagram represents the macro flow of the algorithm in the script. It shows the step-by-step process, including checkpointing, data fetching, saving, and merging operations. The steps are now arranged vertically and in ascending order from left to right.
