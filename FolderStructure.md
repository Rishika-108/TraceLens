client/
│
├── public/
│
├── src/
│
├── components/
│   │
│   ├── common/
│   │
│   ├── dashboard/
│   │
│   ├── evidence/
│   │   ├── EvidenceUpload.jsx
│   │   ├── EvidenceList.jsx
│   │   └── ArtifactViewer.jsx
│   │
│   ├── entities/
│   │   ├── EntityTable.jsx
│   │   └── EntityCard.jsx
│   │
│   ├── timeline/
│   │   ├── Timeline.jsx
│   │   └── TimelineEvent.jsx
│   │
│   ├── graph/
│   │   ├── GraphView.jsx
│   │   └── RelationshipMap.jsx
│   │
│   ├── search/
│   │   ├── SemanticSearch.jsx
│   │   └── SearchResults.jsx
│   │
│   └── reports/
│       ├── ReportViewer.jsx
│       └── ReportGenerator.jsx
│
├── pages/
│   ├── Dashboard.jsx
│   ├── Case.jsx
│   ├── Investigation.jsx
│   └── Report.jsx
│
├── services/
│   ├── api.js
│   ├── evidence.js
│   ├── search.js
│   └── reports.js
│
├── hooks/
│
├── context/
│
├── utils/
│
└── package.json

server/
│
├── app/
│   │
│   ├── api/
│   │   │
│   │   ├── routes/
│   │   │   ├── cases.py
│   │   │   ├── evidence.py
│   │   │   ├── entities.py
│   │   │   ├── relationships.py
│   │   │   ├── timelines.py
│   │   │   ├── investigations.py
│   │   │   ├── search.py
│   │   │   └── reports.py
│   │   │
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── session.py
│   │   └── migrations/
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   ├── repositories/
│   │
│   ├── pipelines/
│   │
│   ├── parsers/
│   │
│   ├── ai/
│   │
│   ├── tasks/
│   │
│   └── utils/
│
├── tests/
│
├── requirements.txt
│
└── Dockerfile

models/
│
├── case.py
├── evidence.py
├── artifact.py
├── entity.py
├── relationship.py
├── timeline.py
└── report.py

tasks/
│
├── parse_evidence.py
├── extract_entities.py
├── build_timeline.py
├── generate_embeddings.py
└── generate_report.py

ai/
│
├── embeddings/
│
├── retrieval/
│
├── agents/
│
├── prompts/
│
└── evaluation/

pipelines/
│
├── ingestion.py
├── normalization.py
├── entity_extraction.py
├── relationship_discovery.py
├── timeline_reconstruction.py
├── embedding_generation.py
└── reporting.py

parsers/
│
├── call_parser.py
├── sms_parser.py
├── email_parser.py
├── whatsapp_parser.py
├── browser_parser.py
└── document_parser.py