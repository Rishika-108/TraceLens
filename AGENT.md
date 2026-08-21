AGENT.md — TraceLens
Authoritative project context for AI coding agents and developers

TraceLens is an AI-assisted digital forensics investigation platform that transforms raw digital evidence into searchable, explainable, and verifiable case intelligence.

This document combines:

The written TraceLens project specification supplied by the developer.

The six-page TraceLens architecture/design PDF supplied with the project.

The repository structure supplied by the developer.

Where the written specification and PDF differ, this document preserves the distinction instead of silently inventing a reconciliation. In particular, the PDF establishes the HLD/LLD, asynchronous processing, RAG flow, and initial ER model, while the supplied repository tree contains additional planned parser modules such as WhatsApp and browser parsing.

1. Project Identity
Name
TraceLens

Category
AI-powered / AI-assisted digital forensics investigation platform.

One-line description
TraceLens is an AI-assisted investigation platform that transforms raw digital evidence into searchable, explainable, and verifiable case intelligence.

Central product idea
TraceLens does not attempt to replace investigators.

Its purpose is to reduce the cognitive and operational burden of examining large collections of fragmented digital artifacts by converting them into:

structured artifacts,

normalized records,

entities,

relationships,

chronological events,

semantic search indexes,

investigation context,

and evidence-backed reports.

The core product principle is:

AI assists discovery and synthesis; evidence remains the source of truth.

2. Source of This Architecture
The project design was supplied in two forms.

2.1 Written specification
The written specification defines:

the problem,

the overall workflow,

supported evidence categories,

entity extraction,

relationship discovery,

timeline reconstruction,

semantic evidence retrieval,

AI-assisted investigation,

explainable AI,

technology choices,

frontend/backend structure,

pipeline modules,

parsers,

AI modules,

and the intended résumé-level engineering outcomes.

2.2 Architecture/design PDF
The supplied six-page PDF contains handwritten HLD, LLD, ER, asynchronous-processing, RAG, and architecture notes.

The PDF establishes several concrete concepts that must be preserved:

Investigator-facing frontend

Evidence upload

Timeline explorer

Relationship graph

Search interface

Investigation console

FastAPI backend

Evidence pipeline

Investigator AI

Report generator

PostgreSQL

pgvector

Redis

File storage

Evidence ingestion

File storage

Parser engine

Data normalization

Event store

Entity extraction

Relationship builder

Timeline engine

Embedding generator

Investigation agent

Report generation

Redis queue

Celery workers

RAG flow

Context builder

LLM

Explainable investigation

Evidence references

Relational entities including Case, Evidence, Artifact, Event, Entity, Relationship, and Reference

The PDF's page content is visual/handwritten rather than machine-readable, so the architectural interpretation should follow the visible diagrams rather than inventing details not shown there.

3. Problem Definition
Modern digital investigations may contain large quantities of heterogeneous digital evidence:

Call logs

SMS messages

Chat exports

Emails

Browser history

Documents

Images

Device metadata

The difficulty is not simply storing these artifacts.

The difficult engineering problem is turning fragmented evidence into a coherent investigation representation.

Investigators need to answer questions such as:

Who communicated with whom?

When did communication happen?

Which events are connected?

What is the chronological sequence?

Which artifacts refer to the same entity?

What relationships exist?

Which evidence supports a hypothesis?

Can an AI-generated conclusion be independently verified?

TraceLens addresses this through a staged evidence-intelligence pipeline.

4. Core Workflow
The written specification defines the conceptual workflow as:

Evidence Ingestion
        ↓
Artifact Parsing
        ↓
Data Normalization
        ↓
Entity Extraction
        ↓
Relationship Discovery
        ↓
Timeline Reconstruction
        ↓
Semantic Retrieval
        ↓
AI-Assisted Investigation
        ↓
Evidence-Backed Report Generation
The PDF provides a more implementation-oriented version:

Evidence Sources
        ↓
Evidence Ingestion
        ↓
File Storage
        ↓
Parser Engine
        ↓
Data Normalization
        ↓
Event Store
        ↓
┌──────────────┬──────────────────┬───────────────┐
│              │                  │               │
Entity       Relationship       Timeline
Extraction    Builder            Engine
└──────────────┴──────────────────┴───────────────┘
        ↓
Embedding Generator
        ↓
pgvector
        ↓
Investigation Agent
        ↓
Report Generation
These two diagrams describe the same overall system at different abstraction levels.

5. Architectural Mental Model
TraceLens can be understood as progressively transforming information:

Raw Evidence
      ↓
Parsed Artifacts
      ↓
Normalized Data
      ↓
Events
      ↓
Entities + Relationships
      ↓
Timeline
      ↓
Embeddings
      ↓
Retrieved Evidence
      ↓
Investigation Context
      ↓
AI-Assisted Investigation
      ↓
Evidence References
      ↓
Report
The architecture must preserve the ability to trace derived information backward toward its source.

6. High-Level Architecture
The PDF's HLD is centered around the investigator:

                     Investigator
                          │
                          ▼
                    Frontend
                          │
          ┌───────────────┼────────────────┐
          │               │                │
   Evidence Upload   Timeline Explorer   Relationship Graph
          │               │                │
          └───────────────┼────────────────┘
                          │
                 Search Interface
                          │
                 Investigation Console
                          │
                          ▼
                     FastAPI
                      Backend
                          │
             ┌────────────┼─────────────┐
             │            │             │
      Evidence Pipeline  Investigator AI  Report Generator
             │            │             │
             └────────────┼─────────────┘
                          ▼
                      Data Layer
             ┌────────────┼─────────────┐
             │            │             │
        PostgreSQL     pgvector       Redis
             │
        File Storage
The exact visual grouping in the handwritten HLD should be treated as conceptual architecture rather than as a rigid deployment topology.

7. Major System Components
TraceLens contains these major conceptual components:

Investigator frontend

FastAPI backend

Evidence ingestion

File storage

Parser engine

Data normalization

Event store

Entity extraction

Relationship builder

Timeline engine

Embedding generation

pgvector semantic retrieval

Investigation agent

Report generator

Redis queue

Celery workers

PostgreSQL

AI/RAG orchestration

Evaluation

Evidence references

8. Technology Stack
The written specification proposes:

Layer	Technology
Frontend	React or Next.js
Backend	FastAPI
Database	PostgreSQL
ORM	SQLAlchemy
Vector search	pgvector
Cache / queue infrastructure	Redis
AI orchestration	Pydantic AI or LangGraph
Background tasks	Celery
Deployment	Docker
The PDF specifically depicts:

FastAPI

PostgreSQL

pgvector

Redis

File Storage

Celery workers

LLM

Parser tools

Entity tools

Embedding tools

Therefore, these components form the core architectural vocabulary of TraceLens.

9. Frontend Architecture
The frontend is the investigator-facing application.

The PDF explicitly identifies these investigator-facing capabilities:

Evidence upload

Timeline explorer

Relationship graph

Search interface

Investigation console

The supplied repository structure expands these into reusable React components and pages.

10. Frontend Repository Structure
client/
│
├── public/
│
├── src/
│
├── components/
│   ├── common/
│   ├── dashboard/
│   ├── evidence/
│   │   ├── EvidenceUpload.jsx
│   │   ├── EvidenceList.jsx
│   │   └── ArtifactViewer.jsx
│   ├── entities/
│   │   ├── EntityTable.jsx
│   │   └── EntityCard.jsx
│   ├── timeline/
│   │   ├── Timeline.jsx
│   │   └── TimelineEvent.jsx
│   ├── graph/
│   │   ├── GraphView.jsx
│   │   └── RelationshipMap.jsx
│   ├── search/
│   │   ├── SemanticSearch.jsx
│   │   └── SearchResults.jsx
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
├── context/
├── utils/
└── package.json
11. Evidence UI
EvidenceUpload.jsx
Responsible for initiating evidence ingestion.

Supported evidence categories from the written specification include:

Call records

Chat messages

Emails

Documents

Images

Browser artifacts

The PDF's parser diagram explicitly shows:

Call

SMS

Email

Document

Image

The repository additionally specifies:

WhatsApp

Browser

Therefore:

PDF-supported source types are architectural baseline.

WhatsApp and browser support are repository-level planned extensions.

Do not claim that the PDF itself specifies WhatsApp/browser parsers.

EvidenceList.jsx
Displays evidence associated with a case.

Evidence should expose processing state where appropriate.

A useful conceptual lifecycle is:

Uploaded
    ↓
Queued
    ↓
Processing
    ↓
Parsed
    ↓
Normalized
    ↓
Indexed
    ↓
Ready
If a stage fails, the state must communicate the failure instead of silently presenting incomplete data as complete.

ArtifactViewer.jsx
Provides access to parsed/normalized artifacts.

The artifact viewer is important for explainability because investigation results should be traceable back to the artifact from which they were derived.

12. Entity UI
EntityTable.jsx
Displays extracted entities.

Supported conceptual categories include:

People

Organizations

Locations

Dates

Phone numbers

Email addresses

EntityCard.jsx
Displays details about an entity and its connections.

The intended navigation pattern is:

Entity
   ↓
Related artifacts
   ↓
Relationships
   ↓
Timeline events
   ↓
Investigation results
13. Timeline UI
Timeline.jsx
Displays reconstructed chronological events.

The written specification identifies timeline reconstruction as the project's most important feature.

Example:

09:45 PM → Phone call
10:01 PM → WhatsApp message
10:14 PM → Email sent
10:27 PM → Browser search
10:42 PM → File downloaded
The exact event types shown depend on the available evidence.

TimelineEvent.jsx
Represents a single event.

Conceptually it should expose:

Timestamp

Event type

Actor/source

Target where applicable

Associated entities

Source artifact

Relevant metadata

Provenance/reference

The PDF's ER notes identify an EVENT entity containing:

id
event_type
timestamp
actor
target
source
This is an important domain-level model.

14. Graph UI
GraphView.jsx
Provides visual exploration of relationships.

RelationshipMap.jsx
Displays entity-to-entity connections.

Example:

Alice
  │
  ▼
WhatsApp
  │
  ▼
Bob
  │
  ▼
Email
  │
  ▼
Charlie
The graph exists to reveal connections that may not be obvious when artifacts are inspected independently.

15. Search UI
SemanticSearch.jsx
Provides natural-language semantic retrieval.

Example:

Find all conversations related to financial transactions.
SearchResults.jsx
Displays retrieved evidence and contextual information.

Search results must retain links to the underlying artifacts/evidence.

16. Investigation Console
The PDF explicitly identifies an Investigation Console in the frontend.

The written specification gives examples of natural-language investigative queries:

Who contacted Bob after August 15?

Show all conversations mentioning payments.

Generate a timeline for the suspect.

Identify all interactions involving this phone number.
The console is the user-facing entry point to the RAG/investigation system.

17. Reports UI
ReportViewer.jsx
Displays generated reports.

ReportGenerator.jsx
Initiates report generation.

Reports should distinguish between:

Observed evidence
       ↓
Derived intelligence
       ↓
AI interpretation
These should not be silently presented as equivalent.

18. Frontend Pages
Dashboard.jsx
High-level case overview.

Case.jsx
Primary case workspace.

Conceptually:

Case
 ├── Evidence
 ├── Entities
 ├── Relationships
 ├── Timeline
 ├── Search
 ├── Investigation
 └── Reports
Investigation.jsx
Natural-language investigative workspace.

Report.jsx
Report review and presentation interface.

19. Frontend Services
services/
├── api.js
├── evidence.js
├── search.js
└── reports.js
These services isolate frontend API communication from presentation components.

20. Backend Architecture
The backend is built around FastAPI.

The supplied architecture separates:

API
 ↓
Application Services
 ↓
Repositories / Data Access
 ↓
Database
and:

API
 ↓
Background Tasks
 ↓
Processing Pipelines
 ↓
Parsers / AI
 ↓
Derived Intelligence
Route handlers should not become the location for complex domain logic.

21. Backend Repository Structure
server/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── cases.py
│   │   │   ├── evidence.py
│   │   │   ├── entities.py
│   │   │   ├── relationships.py
│   │   │   ├── timelines.py
│   │   │   ├── investigations.py
│   │   │   ├── search.py
│   │   │   └── reports.py
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
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── pipelines/
│   ├── parsers/
│   ├── ai/
│   ├── tasks/
│   └── utils/
│
├── tests/
├── requirements.txt
└── Dockerfile
22. API Routes
cases.py
Case-level operations.

evidence.py
Evidence ingestion, metadata, processing state, and retrieval.

entities.py
Entity retrieval and entity-oriented investigation operations.

relationships.py
Relationship access and graph-oriented operations.

timelines.py
Timeline/event retrieval.

investigations.py
Natural-language investigation workflow.

search.py
Semantic evidence retrieval.

reports.py
Report generation and retrieval.

23. Core Backend
config.py
Centralized configuration.

Secrets, database URLs, AI configuration, and infrastructure settings should not be hardcoded.

security.py
Authentication, authorization, and security-related application logic.

TraceLens handles sensitive evidence and must treat access control as a first-class concern.

logging.py
Centralized application logging.

Avoid logging complete sensitive evidence contents merely for debugging convenience.

24. Database Architecture
The PDF's data layer explicitly identifies:

PostgreSQL
pgvector
Redis
File Storage
PostgreSQL is the primary structured data store.

pgvector supports vector representations and semantic similarity retrieval.

Redis participates in asynchronous processing/queue infrastructure.

File storage holds source evidence files or file references.

25. ER Model
The PDF sketches a relational model containing:

CASE
EVIDENCE
ARTIFACT
EVENT
ENTITY
RELATIONSHIP
REFERENCE
The handwritten diagram provides the following fields.

25.1 CASE
Case
├── id (PK)
├── title
├── description
└── created_at
Relationships shown in the PDF indicate that evidence belongs to a case.

25.2 EVIDENCE
Evidence
├── id (PK)
├── case_id (FK)
├── filename
├── file_type
├── file_path
└── uploaded_at
Evidence is the source-level object associated with an investigation case.

25.3 ARTIFACT
Artifact
├── id (PK)
├── evidence_id (FK)
├── raw_data
├── parsed_data
└── parser_stage
An artifact represents parsed content derived from source evidence.

Conceptually:

Evidence
   ↓
Artifact
   ↓
Events / Entities / Relationships / Embeddings
25.4 EVENT
The PDF sketches:

Event
├── id (PK)
├── event_type
├── timestamp
├── actor
├── target
└── source
Events are central to timeline reconstruction.

25.5 ENTITY
The PDF sketches:

Entity
├── id (PK)
├── entity_type
└── value
25.6 RELATIONSHIP
The PDF sketches:

Relationship
├── id (PK)
├── source_entity_id
├── target_entity_id
└── relationship_type
This is the basis for the relationship graph.

25.7 REFERENCE
The PDF sketches:

Reference
├── id (PK)
└── content
The handwritten diagram's exact relationship/cardinality around REFERENCE is not sufficiently precise to infer additional schema constraints.

Do not invent them without an explicit design decision.

26. Event Store
The PDF explicitly introduces an Event Store after normalization:

Evidence
   ↓
Parser Engine
   ↓
Data Normalization
   ↓
Event Store
   ↓
Entity Extraction
Relationship Builder
Timeline Engine
This is an important architectural concept.

The Event Store provides a normalized event-oriented representation that downstream investigation capabilities can operate over.

Do not collapse the Event Store concept into "just the timeline."

The timeline is one consumer/representation of event data.

27. Evidence Pipeline
The evidence-processing pipeline follows:

Evidence Source
       ↓
Evidence Ingestion
       ↓
File Storage
       ↓
Parser Engine
       ↓
Data Normalization
       ↓
Event Store
       ↓
Derived Intelligence
The evidence pipeline is responsible for transforming heterogeneous external evidence into internally usable structured data.

28. Parser Engine
The PDF explicitly identifies a Parser Engine containing:

Call Parser
SMS Parser
Email Parser
Document Parser
Image Parser
The supplied repository additionally contains:

WhatsApp Parser
Browser Parser
Therefore the intended implementation repository is:

parsers/
├── call_parser.py
├── sms_parser.py
├── email_parser.py
├── whatsapp_parser.py
├── browser_parser.py
└── document_parser.py
The difference must be understood as:

PDF baseline
+
Repository-specified extensions
not as contradictory evidence.

29. Parser Responsibilities
Each parser should understand the structure of its source format and emit data suitable for normalization.

A parser should not be responsible for:

case-wide investigation,

global relationship reasoning,

semantic retrieval,

report generation,

or unconstrained AI reasoning.

The parser's responsibility is source interpretation.

30. Data Normalization
The normalization layer converts source-specific records into a common representation.

Conceptually:

Call record
SMS
Email
Chat
Browser event
Document event
        ↓
Common normalized representation
        ↓
Event Store
The purpose is to prevent downstream services from having to understand every raw evidence format independently.

31. Entity Extraction
The system extracts important entities from normalized artifacts.

Supported examples:

People

Organizations

Locations

Dates

Phone numbers

Email addresses

Example:

"Meet John near MG Road tomorrow at 6 PM."

        ↓

Person → John
Location → MG Road
Time → 6 PM
Entity provenance should be preserved.

32. Relationship Discovery / Relationship Builder
The written specification calls this Relationship Discovery.

The PDF calls the corresponding component a Relationship Builder.

Its purpose is to connect extracted entities.

Example:

Alice
  │
  ▼
WhatsApp
  │
  ▼
Bob
  │
  ▼
Email
  │
  ▼
Charlie
The relationship graph must remain grounded in artifacts/events from which the relationship was derived.

33. Timeline Engine
The PDF calls this component the Timeline Engine.

The written specification calls the broader capability Timeline Reconstruction.

The engine uses event information to construct chronological sequences.

Example:

09:45 PM → Phone call
10:01 PM → WhatsApp message
10:14 PM → Email sent
10:27 PM → Browser search
10:42 PM → File downloaded
Do not invent timestamp precision when the source evidence does not provide it.

34. Embedding Generator
The PDF explicitly places the Embedding Generator after structured event/entity/relationship processing.

Conceptual flow:

Relevant normalized content
        ↓
Embedding Generator
        ↓
Vector
        ↓
pgvector
Embeddings are retrieval infrastructure.

They are not themselves evidence.

35. Background Processing
The PDF explicitly describes asynchronous processing.

Architecture:

Investigator
      ↓
Upload Evidence
      ↓
FastAPI
      ↓
Redis Queue
      ├── Parser Tool → Celery Worker
      ├── Entity Tool → Celery Worker
      └── Embedding Tool → Celery Worker
                       ↓
                   PostgreSQL
The repository defines:

tasks/
├── parse_evidence.py
├── extract_entities.py
├── build_timeline.py
├── generate_embeddings.py
└── generate_report.py
This means processing should be designed around background jobs where appropriate.

36. Celery Tasks
parse_evidence.py
Runs evidence parsing asynchronously.

extract_entities.py
Runs entity extraction asynchronously.

build_timeline.py
Builds timeline data.

generate_embeddings.py
Generates vector representations.

generate_report.py
Generates reports.

The PDF explicitly depicts parser, entity, and embedding work as worker-based processing. The repository additionally defines timeline and report tasks.

37. Redis
Redis participates in the asynchronous processing architecture.

Conceptually:

FastAPI
   ↓
Redis Queue
   ↓
Celery Worker
Do not use Redis merely as an arbitrary cache if the implementation is intended to follow the PDF architecture.

Caching may be added where justified, but the PDF's primary role is queue/task infrastructure.

38. Celery
Celery provides background execution for expensive or long-running work.

Candidate workloads include:

Evidence parsing

Entity extraction

Timeline construction

Embedding generation

Report generation

The API should not remain blocked while these operations execute.

39. RAG Architecture
The PDF contains a dedicated TraceLens RAG pipeline:

Investigator
      ↓
Natural-language Query
      ↓
Embedding Generator
      ↓
pgvector
      ↓
Semantic Similarity
      ↓
Evidence Retrieval
      ↓
Context Builder
      ↓
LLM
      ↓
Explainable Investigation
      ↓
Evidence References
This is one of the defining architectural flows of TraceLens.

40. Semantic Retrieval
Traditional keyword search can fail when different terminology expresses the same concept.

Example query:

Find all conversations related to financial transactions.
Potentially relevant evidence:

"Transfer the amount."
"Send the payment."
"The money has been deposited."
Semantic embeddings allow retrieval based on meaning rather than exact lexical overlap.

41. Vector Search
The retrieval flow is:

Natural-language query
        ↓
Query embedding
        ↓
pgvector similarity search
        ↓
Relevant evidence/artifacts
The vector store must remain associated with source evidence so that retrieved vectors can be mapped back to inspectable artifacts.

42. Context Builder
The PDF explicitly introduces a Context Builder between evidence retrieval and the LLM.

Therefore the RAG flow is not simply:

Vector search → LLM
It is:

Query
  ↓
Embedding
  ↓
Similarity search
  ↓
Evidence retrieval
  ↓
Context Builder
  ↓
LLM
The Context Builder should prepare relevant retrieved evidence for reasoning while preserving source identity.

43. Investigation Agent
The repository defines:

ai/
└── agents/
    └── investigator.py
The PDF calls this the Investigation Agent.

It processes natural-language investigative questions using retrieved case context.

Example:

"Who contacted Bob after August 15?"
Conceptually:

Question
   ↓
Retrieve evidence
   ↓
Build context
   ↓
Investigation Agent
   ↓
Evidence-backed answer
The agent must not answer case-specific questions from general model memory.

44. Explainable Investigation
The PDF explicitly places:

LLM
 ↓
Explainable Investigation
 ↓
Evidence References
This means explanation is a first-class stage of the investigation workflow.

The system should make clear:

what was found,

why it matters,

which evidence supports it,

and where the investigator can inspect that evidence.

45. Evidence References
Evidence references are a defining TraceLens feature.

Bad:

This conversation is suspicious.
Better:

Suspicious communication identified.

Evidence:
- SMS at 8:15 PM
- Email at 8:32 PM
- Call at 8:40 PM

Confidence: 91%
The exact confidence number is illustrative.

The important architectural requirement is:

Conclusion
   ↓
Evidence References
   ↓
Inspectable source artifacts
46. AI Is Not the Source of Truth
This is a non-negotiable project principle.

AI-generated:

summaries,

classifications,

hypotheses,

confidence values,

relationship interpretations,

investigative explanations

are derived outputs.

The original evidence remains the source of truth.

47. Fact vs Inference
The system should distinguish:

FACT

A call occurred at 8:40 PM.
from:

INFERENCE

The timing may indicate a relationship between the call
and another event.
The second must not be presented as if it were directly observed evidence.

48. Uncertainty
The system should preserve uncertainty.

If the evidence does not establish:

exact identity,

exact timestamp,

exact relationship,

exact interpretation,

then the output should not manufacture certainty.

A confidence score does not transform uncertain evidence into proof.

49. Investigation Query Examples
The written specification provides:

Who contacted Bob after August 15?

Show all conversations mentioning payments.

Generate a timeline for the suspect.

Identify all interactions involving this phone number.
These represent the intended natural-language investigation interface.

50. Report Generation
The PDF places Report Generation after the Investigation Agent.

The repository contains:

ai/agents/report_agent.py
ai/prompts/report_prompt.py
tasks/generate_report.py
pipelines/reporting.py
The report-generation architecture is therefore:

Case intelligence
       ↓
Investigation result
       ↓
Report Agent
       ↓
Evidence-backed report
51. Report Agent
ai/agents/report_agent.py

The report agent should synthesize structured case information and retrieved evidence into a readable report.

It should not generate unsupported facts merely to make the report sound complete.

52. AI Prompt Layer
ai/prompts/
├── investigation_prompt.py
└── report_prompt.py
Prompts should reinforce:

Evidence grounding

Source attribution

Non-fabrication

Explicit uncertainty

Separation of fact and inference

Evidence references

53. AI Evaluation
The repository defines:

ai/evaluation/
└── evaluator.py
AI evaluation should consider at least conceptually:

Retrieval relevance

Evidence grounding

Correctness

Unsupported claims

Source traceability

Consistency

Appropriate uncertainty

Fluent language alone is not an adequate measure of investigation quality.

54. AI Architecture Directory
ai/
├── embeddings/
│   ├── model.py
│   ├── generator.py
│   └── storage.py
│
├── retrieval/
│   ├── vector_store.py
│   ├── semantic_search.py
│   └── retriever.py
│
├── agents/
│   ├── investigator.py
│   └── report_agent.py
│
├── prompts/
│   ├── investigation_prompt.py
│   └── report_prompt.py
│
└── evaluation/
    └── evaluator.py
55. Embedding Layer
model.py
Defines/configures the embedding model.

generator.py
Generates embeddings.

storage.py
Handles persistence/access of embedding representations.

56. Retrieval Layer
vector_store.py
Abstraction around vector storage/search.

semantic_search.py
Semantic similarity search.

retriever.py
Coordinates retrieval for downstream investigation.

57. Pipelines Directory
pipelines/
├── ingestion.py
├── normalization.py
├── entity_extraction.py
├── relationship_discovery.py
├── timeline_reconstruction.py
├── embedding_generation.py
└── reporting.py
These modules represent application-level processing stages.

58. Pipeline Responsibilities
ingestion.py
Registers and initiates evidence processing.

normalization.py
Converts source-specific parsed structures into common internal forms.

entity_extraction.py
Identifies entities.

relationship_discovery.py
Builds relationships between entities.

timeline_reconstruction.py
Builds chronological representations.

embedding_generation.py
Creates semantic vector representations.

reporting.py
Coordinates report-generation processing.

59. Separation of Responsibilities
Maintain these boundaries:

Parser
    = Understand source format

Normalizer
    = Convert source data into common representation

Event Store
    = Persist normalized event-oriented data

Entity Extractor
    = Identify entities

Relationship Builder
    = Connect entities

Timeline Engine
    = Organize events chronologically

Embedding Generator
    = Create semantic representations

Retriever
    = Find relevant evidence

Context Builder
    = Prepare retrieved evidence for reasoning

Investigation Agent
    = Reason over case context

Report Generator
    = Produce evidence-backed report
Do not collapse these responsibilities into one generic AI service.

60. Complete Evidence-to-Answer Flow
A complete TraceLens investigation can be represented as:

                 RAW EVIDENCE
                      │
                      ▼
               Evidence Ingestion
                      │
                      ▼
                 File Storage
                      │
                      ▼
                Parser Engine
                      │
                      ▼
               Normalization
                      │
                      ▼
                  Event Store
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       Entities   Relationships  Timeline
          │           │            │
          └───────────┼────────────┘
                      ▼
              Embedding Generator
                      │
                      ▼
                   pgvector
                      │
                      ▼
            Natural-language Query
                      │
                      ▼
              Semantic Retrieval
                      │
                      ▼
                Context Builder
                      │
                      ▼
                     LLM
                      │
                      ▼
            Investigation Agent
                      │
                      ▼
          Explainable Investigation
                      │
                      ▼
              Evidence References
                      │
                      ▼
              Report Generation
61. Case-Centric Architecture
A case is the top-level logical boundary.

Conceptually:

Case
 ├── Evidence
 │    └── Artifacts
 │         └── Events
 │
 ├── Entities
 │
 ├── Relationships
 │
 ├── Timeline
 │
 ├── Embeddings
 │
 ├── Investigations
 │
 └── Reports
Case isolation must be preserved throughout APIs, queries, retrieval, background jobs, and AI context.

62. Provenance / Data Lineage
A key invariant is:

Report Claim
    ↓
Investigation Result
    ↓
Retrieved Evidence
    ↓
Artifact
    ↓
Event / Entity / Relationship
    ↓
Original Evidence
Where possible, every derived object should retain enough source information to navigate this chain.

63. Evidence vs Derived Intelligence
Keep these conceptually separate.

RAW / SOURCE
├── Original evidence file
└── Source record

DERIVED
├── Parsed artifact
├── Normalized event
├── Entity
├── Relationship
├── Timeline representation
├── Embedding
├── Investigation result
└── Report
Derived intelligence can be recomputed without replacing the source.

64. Security
TraceLens handles potentially sensitive digital evidence.

Security requirements include:

Authentication

Authorization

Case-level isolation

Least-privilege access

Secure secret management

Restricted evidence access

Safe logging

Controlled AI context

No accidental cross-case retrieval

Do not expose evidence through unrelated API endpoints.

65. AI Data Isolation
When constructing AI prompts/context:

Authorized User
      ↓
Authorized Case
      ↓
Relevant Evidence
      ↓
Relevant Retrieved Context
      ↓
LLM
Do not indiscriminately provide all case evidence to an LLM when only a subset is relevant.

66. File Storage
The PDF explicitly identifies File Storage as part of the data layer and places it after evidence ingestion.

The source file and its metadata should remain distinguishable from parsed artifacts.

Conceptually:

Evidence
   ├── Metadata
   └── Source File
          ↓
       Parser
          ↓
       Artifact
67. Error Handling
Processing should have explicit states.

Conceptually:

PENDING
PROCESSING
COMPLETED
FAILED
Failures must be observable.

A failed parser must not appear to have produced a successful artifact.

A failed embedding task must not silently mark an artifact as searchable.

68. Asynchronous State
For asynchronous processing, the API/UI should be able to distinguish:

Queued
Processing
Completed
Failed
This is particularly important because evidence processing can involve multiple background stages.

69. Observability
Operational logs should make it possible to determine:

which case is being processed,

which evidence item is being processed,

which pipeline stage is active,

which Celery task is running,

whether a task succeeded,

where a failure occurred,

whether retrieval succeeded,

whether AI generation failed.

Do not log complete sensitive evidence contents unnecessarily.

70. Testing Strategy
The repository includes:

server/tests/
Testing should cover:

Parser tests
      ↓
Normalization tests
      ↓
Event-store tests
      ↓
Entity tests
      ↓
Relationship tests
      ↓
Timeline tests
      ↓
Embedding/retrieval tests
      ↓
Service tests
      ↓
API tests
      ↓
AI evaluation
      ↓
End-to-end investigation tests
71. Critical Test Properties
Tests should verify:

Correct parser behavior

Correct normalization

Correct event creation

Entity extraction

Relationship construction

Timeline ordering

Evidence-to-artifact provenance

Semantic retrieval relevance

Case isolation

Evidence references

AI grounding

Unsupported-claim handling

Background task failure behavior

Report generation correctness

72. Parser Extensibility
Adding a new evidence type should follow:

New Evidence Format
       ↓
New Parser
       ↓
Normalized Representation
       ↓
Event Store
       ↓
Existing Entity / Relationship / Timeline Pipeline
       ↓
Embedding / Retrieval
The downstream system should not need to be rewritten for each evidence source.

73. Adding a New Investigation Capability
A new AI investigation capability should follow:

Natural-language question
        ↓
Query interpretation
        ↓
Semantic/structured retrieval
        ↓
Evidence selection
        ↓
Context Builder
        ↓
AI reasoning
        ↓
Evidence references
        ↓
Explainable response
Do not implement:

Question → LLM → unsupported answer
74. Example: Entity Extraction
Input:

"Meet John near MG Road tomorrow at 6 PM."
Pipeline:

Message
   ↓
Parser
   ↓
Normalized artifact
   ↓
Entity extraction
Result:

Person → John
Location → MG Road
Time → 6 PM
The extracted entities should retain their source artifact association.

75. Example: Relationship Discovery
Given:

Alice communicated with Bob through WhatsApp.
Bob communicated with Charlie through email.
The system may represent:

Alice
  │
  └── WhatsApp communication ──> Bob
                                  │
                                  └── Email communication ──> Charlie
The exact relationship semantics should be based on observed evidence rather than invented interpretation.

76. Example: Timeline Reconstruction
Given:

Phone call      09:45 PM
WhatsApp        10:01 PM
Email           10:14 PM
Browser search  10:27 PM
File download   10:42 PM
The timeline engine produces:

09:45 PM → Phone call
10:01 PM → WhatsApp message
10:14 PM → Email sent
10:27 PM → Browser search
10:42 PM → File downloaded
77. Example: Semantic Retrieval
Query:

Find all conversations related to financial transactions.
Possible semantically relevant results:

"Transfer the amount."
"Send the payment."
"The money has been deposited."
The system should return source artifacts rather than only generated paraphrases.

78. Example: RAG Investigation
Query:

Who contacted Bob after August 15?
Architecture:

Query
 ↓
Query embedding
 ↓
pgvector / semantic retrieval
 ↓
Relevant communication artifacts
 ↓
Context Builder
 ↓
Investigation Agent / LLM
 ↓
Answer
 ↓
Evidence References
79. Example: Explainable Output
Bad:

This conversation is suspicious.
Preferred form:

Potentially suspicious communication identified.

Supporting evidence:
- SMS at 8:15 PM
- Email at 8:32 PM
- Call at 8:40 PM

Confidence:
[model/system confidence if available]

Evidence references:
[links/IDs to source artifacts]
The exact language and confidence representation may evolve.

The invariant is evidence traceability.

80. AI Reliability Rules
Rule 1 — Never fabricate evidence
If the evidence does not support an answer, explicitly indicate insufficient evidence.

Rule 2 — Never manufacture evidence references
References must correspond to actual stored evidence/artifacts.

Rule 3 — Separate observation from inference
Do not turn a model interpretation into an observed fact.

Rule 4 — Preserve uncertainty
Do not invent precision.

Rule 5 — Retrieve before reasoning
Case-specific questions should use case evidence.

Rule 6 — Keep investigators in control
The platform assists investigation; it does not establish guilt or replace human judgment.

81. Non-Goals
TraceLens is not:

An autonomous investigator

A replacement for human investigators

A system for establishing guilt

A system that manufactures evidence

A generic chatbot detached from case data

A black-box prediction engine

Its purpose is evidence-centered investigative assistance.

82. Repository-to-Architecture Mapping
Repository area	Architectural responsibility
client/components/evidence	Evidence interaction
client/components/timeline	Timeline explorer
client/components/graph	Relationship graph
client/components/search	Semantic search
client/components/reports	Report presentation
client/pages/Investigation.jsx	Investigation console
server/api/routes	FastAPI API
server/parsers	Parser engine
server/pipelines/normalization.py	Data normalization
server/models	Domain/database model layer
server/tasks	Background processing
server/ai/embeddings	Embedding generation/storage
server/ai/retrieval	Semantic retrieval
server/ai/agents/investigator.py	Investigation agent
server/ai/agents/report_agent.py	Report generation
server/ai/prompts	AI instruction layer
server/ai/evaluation	AI evaluation
server/repositories	Persistence abstraction
server/services	Application/domain coordination
server/db	PostgreSQL/session/migration infrastructure
83. Important Terminology
Use the following terms consistently.

Term	Meaning
Evidence	Original source material supplied to the case
Artifact	Parsed item derived from evidence
Event	Normalized occurrence with temporal/contextual information
Entity	Person, organization, location, phone, email, etc.
Relationship	Connection between entities
Event Store	Normalized event-oriented persistence layer
Timeline	Chronological representation of events
Embedding	Vector representation used for semantic retrieval
pgvector	PostgreSQL vector-search extension/storage mechanism
Retrieval	Selecting relevant evidence for a query
Context Builder	Constructs LLM-ready context from retrieved evidence
Investigation Agent	AI component that reasons over case evidence
Evidence Reference	Link/identifier allowing verification of a conclusion
Report	Structured output derived from case intelligence
84. Design Invariants
The following invariants should guide implementation.

Invariant 1
Every case-specific AI answer must be grounded in case data.

Invariant 2
Every important conclusion should be traceable to supporting evidence.

Invariant 3
Raw evidence should remain distinguishable from derived intelligence.

Invariant 4
Long-running evidence-processing operations should be suitable for asynchronous execution.

Invariant 5
Parser-specific knowledge should not leak unnecessarily into downstream stages.

Invariant 6
Case boundaries must be respected by storage, retrieval, background processing, and AI context.

Invariant 7
Timeline events must retain source/provenance information where possible.

Invariant 8
Semantic retrieval must return inspectable evidence, not only generated text.

Invariant 9
AI confidence is not equivalent to evidentiary proof.

Invariant 10
When the evidence is insufficient, the system must say so.

85. Development Workflow
For a new feature:

1. Define domain behavior
2. Identify affected evidence/data structures
3. Update model/schema if necessary
4. Define repository behavior
5. Implement service logic
6. Implement pipeline/task behavior
7. Expose API
8. Implement frontend service
9. Implement UI
10. Add tests
11. Verify provenance
12. Verify failure states
13. Verify AI grounding if AI is involved
14. Validate case isolation
Do not begin with UI behavior that has no defined backend/data contract.

86. Adding a New Evidence Type
Procedure:

1. Define source format
2. Implement parser
3. Normalize output
4. Create/store appropriate events
5. Preserve source linkage
6. Integrate entity extraction
7. Integrate relationship discovery
8. Integrate timeline processing
9. Integrate embeddings
10. Integrate retrieval
11. Add parser tests
12. Add pipeline/integration tests
87. Adding a New AI Feature
Procedure:

1. Define the investigative question
2. Determine required evidence
3. Define retrieval strategy
4. Define context structure
5. Define AI reasoning behavior
6. Define evidence-reference format
7. Define failure/insufficient-evidence behavior
8. Implement evaluation
9. Implement API
10. Implement UI
11. Test with representative evidence
88. Definition of Done
A feature is not complete simply because the UI renders.

A feature is complete when:

Domain behavior is defined.

API contract is explicit.

Persistence behavior is correct.

Background processing behavior is explicit where required.

Failure states are handled.

Evidence provenance is preserved.

Case isolation is preserved.

AI output is grounded where applicable.

Evidence references are available where applicable.

Tests exist.

Frontend loading/error/success states work.

Realistic case data can pass through the feature.

The system does not silently invent information.

89. Engineering Trade-offs
Structured database + vector search
TraceLens uses both PostgreSQL and pgvector because structured investigation data and semantic retrieval solve different problems.

PostgreSQL
    ↓
Cases / Evidence / Events / Entities / Relationships / Reports

pgvector
    ↓
Semantic representations / similarity retrieval
Do not force every investigation query into vector search.

Likewise, do not expect keyword/relational queries to replace semantic retrieval for meaning-based searches.

90. Deterministic vs AI Processing
Prefer deterministic processing where the source provides structured information.

Example:

Timestamp in source
     ↓
Store timestamp
rather than asking an LLM to infer it.

Use AI where semantic interpretation provides value:

Free-form text
     ↓
Entity extraction
or:

Natural-language investigation
     ↓
Evidence retrieval + reasoning
The architecture should use AI selectively rather than treating AI as a universal parser.

91. Source of Truth Hierarchy
When deciding what to trust:

Original Evidence
      ↓
Parsed / Normalized Evidence
      ↓
Structured Derived Data
      ↓
Retrieved Context
      ↓
AI Interpretation
      ↓
Generated Report
Higher layers must not silently override lower layers.

92. Project Value Proposition
TraceLens demonstrates a combination of:

Backend engineering
FastAPI

REST API design

PostgreSQL

SQLAlchemy

Repositories

Services

Background jobs

Redis

Celery

Docker

AI engineering
Embeddings

pgvector

Semantic search

RAG

Context construction

Investigation agents

Report agents

Prompt engineering

AI evaluation

Data/system design
Heterogeneous ingestion

Parser architecture

Normalization

Event stores

Entity extraction

Relationship graphs

Timeline reconstruction

Provenance

Human-in-the-loop verification

Explainable AI

93. Architecture Summary
The complete architecture is:

                           INVESTIGATOR
                                │
                                ▼
                        React / Next.js
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
 Evidence Upload          Timeline Explorer      Relationship Graph
        │                       │                        │
 Search Interface        Investigation Console      Reports
        └───────────────────────┼────────────────────────┘
                                │
                                ▼
                             FastAPI
                                │
                ┌───────────────┼────────────────┐
                │               │                │
                ▼               ▼                ▼
        Evidence Pipeline  Investigator AI  Report Generator
                │
                ▼
          File Storage
                │
                ▼
          Parser Engine
                │
                ▼
        Data Normalization
                │
                ▼
            Event Store
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
     Entities Relations Timeline
        │       │        │
        └───────┼────────┘
                ▼
       Embedding Generator
                │
                ▼
             pgvector
                │
                ▼
      Semantic Evidence Retrieval
                │
                ▼
          Context Builder
                │
                ▼
               LLM
                │
                ▼
      Explainable Investigation
                │
                ▼
       Evidence References
                │
                ▼
         Report Generation

Asynchronous infrastructure:

FastAPI
   ↓
Redis Queue
   ↓
Celery Workers
   ├── Parser
   ├── Entity Extraction
   ├── Timeline Processing
   ├── Embedding Generation
   └── Report Generation
94. Final Definition
TraceLens is an evidence-centered AI investigation platform.

Its purpose is to transform:

Thousands of fragmented digital artifacts
into:

A searchable, structured, chronological,
relational, explainable, and verifiable
investigation workspace.
The system achieves this through:

Ingestion
  ↓
Parsing
  ↓
Normalization
  ↓
Event Store
  ↓
Entity Extraction
  ↓
Relationship Discovery
  ↓
Timeline Reconstruction
  ↓
Embeddings
  ↓
Semantic Retrieval
  ↓
Context Building
  ↓
Investigation Agent
  ↓
Explainable Investigation
  ↓
Evidence References
  ↓
Report Generation
The defining principle is:

TraceLens does not replace investigators. It reduces thousands of fragmented digital artifacts into a structured, explainable, and evidence-backed investigation workflow.

Any implementation decision that strengthens evidence traceability, explainability, verifiability, case isolation, and investigator control is aligned with the architecture.

Any implementation that makes the platform dependent on unsupported AI inference, loses provenance, mixes unrelated cases, or treats generated text as the source of truth should be treated as an architectural regression.

