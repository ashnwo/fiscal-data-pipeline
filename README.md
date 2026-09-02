cat > README.md << 'EOF'
# Fiscal Data Pipeline

Daily-batch data pipeline ingesting U.S. Treasury Debt to the Penny data 
from the Fiscal Data API, transforming through a medallion architecture 
(raw → curated → analytics), and surfacing through a BI layer.

## Stack
- Ingestion: Python (`requests`)
- Storage: AWS S3 (raw + curated zones)
- Transform: PySpark
- Warehouse: Snowflake
- Modeling: dbt
- Orchestration: Airflow
- BI: Power BI

## Status
<!-- Walking skeleton in progress. See `ingest.py` for current state. -->
Current status: Bronze layer complete, Silver in progress

# Architecture Diagram
```mermaid
flowchart LR
    A[Treasury Fiscal Data API<br/>debt_to_penny] --> B[ingest.py<br/>paginated fetch]
    B --> C[Local raw landing<br/>date-partitioned]
    C -->|pandas clean<br/>+ Snowflake load| E[(BRONZE<br/>raw typed)]
    E -.->|PySpark| F[(SILVER<br/>conformed)]
    F -.->|dbt| G[(GOLD<br/>business analytics)]
    G -.-> H[Power BI<br/>dashboard]

    I[Airflow] -.-> B
    I -.-> E
    I -.-> F
    I -.-> G

    classDef bronze fill:#cd7f32,color:#fff,stroke:#8b5a2b
    classDef silver fill:#c0c0c0,color:#000,stroke:#888
    classDef gold fill:#d4af37,color:#000,stroke:#aa8c2c

    class E bronze
    class F silver
    class G gold
```