# Architecture Diagrams

## System Component Diagram (Mermaid)
```mermaid
flowchart LR
  subgraph Clients
    U[Users]
    Dev[Developers]
  end

  U -->|HTTP/WS| API
  Dev -->|CI/CD| GH[GitHub Actions]

  subgraph Kubernetes Cluster
    API[API Service]
    ALM[Agent Lifecycle Manager]
    KDD[Knowledge Drift Detector]
    SHM[Self-Healing Monitor]
    RQ[(RabbitMQ)]
    PM[Prometheus Operator]
    GF[Grafana]
  end

  API -->|SQL| PG[(Postgres)]
  API -->|Bolt| NEO[(Neo4j)]

  ALM <-->|AMQP| RQ
  KDD <-->|AMQP| RQ
  SHM <-->|AMQP| RQ

  PM -->|scrape| API
  PM -->|scrape| ALM
  PM -->|scrape| KDD
  PM -->|scrape| SHM
  PM --> GF

  GH -->|kubectl apply -k| Kubernetes Cluster
```

## Request Flow (Mermaid Sequence)
```mermaid
sequenceDiagram
  participant User
  participant API
  participant Postgres as PG
  participant Neo4j as NEO
  participant RabbitMQ as RQ

  User->>API: HTTP request
  API->>PG: Query/Write
  API->>NEO: Graph query
  API-->>User: Response
  API->>RQ: Publish event (optional)
```

## PlantUML (Component Diagram)
```plantuml
@startuml
package "NeoV3" {
  [API Service] --> [Postgres]
  [API Service] --> [Neo4j]
  [API Service] ..> (ServiceMonitor)
  [Agent Lifecycle] --> (RabbitMQ)
  [Knowledge Drift] --> (RabbitMQ)
  [Self-Healing] --> (RabbitMQ)
  (Prometheus) ..> [API Service]
  (Prometheus) ..> [Agent Lifecycle]
  (Prometheus) ..> [Knowledge Drift]
  (Prometheus) ..> [Self-Healing]
}
@enduml
```

Notes:
- Mermaid renders on GitHub natively.
- PlantUML block can be exported via IDE plugins or CI tools if needed.
