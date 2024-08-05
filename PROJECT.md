# Project Flow Diagram

```mermaid
graph TD
    A[Start]
    B[Load Checkpoint]
    C{Check Current Step}
    AB[End]

    A --> B
    B --> C

    subgraph Step1
    D[Fetch IX Data]
    E[Save IX Data]
    F[Update Progress]
    G[Save Checkpoint]
    end

    subgraph Step2
    H[Fetch IXFAC Data]
    I[Save IXFAC Data]
    J[Update Progress]
    K[Save Checkpoint]
    end

    subgraph Step3
    L[Fetch FAC Data]
    M[Save FAC Data]
    N[Save Checkpoint]
    end

    subgraph Step4
    O[Merge IXFAC and FAC Data]
    P[Save Merged Data]
    Q[Save Checkpoint]
    end

    subgraph Step5
    R[Fetch NETIXLAN Data]
    S[Save NETIXLAN Data]
    T[Update Progress]
    U[Save Checkpoint]
    end

    subgraph Step6
    V[Fetch NET Data]
    W[Save NET Data]
    X[Save Checkpoint]
    end

    subgraph Step7
    Y[Merge NETIXLAN and NET Data]
    Z[Save Merged Data]
    AA[Save Checkpoint]
    end

    C -->|Step 1| D
    D --> E --> F --> G --> C

    C -->|Step 2| H
    H --> I --> J --> K --> C

    C -->|Step 3| L
    L --> M --> N --> C

    C -->|Step 4| O
    O --> P --> Q --> C

    C -->|Step 5| R
    R --> S --> T --> U --> C

    C -->|Step 6| V
    V --> W --> X --> C

    C -->|Step 7| Y
    Y --> Z --> AA --> C

    C -->|Step > 7| AB
```

This diagram represents the macro flow of the algorithm in the script. It shows the step-by-step process, including checkpointing, data fetching, saving, and merging operations.
