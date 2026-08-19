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