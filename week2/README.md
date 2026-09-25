## Week 2 — Build the History Brain

Week 2 converts my WhatsApp chat history into searchable conversation memory. The historical messages are cleaned into **“Their message → My reply”** pairs, mapped to relationships, converted into vector embeddings using `paraphrase-multilingual-mpnet-base-v2`, and stored in relationship-specific ChromaDB collections. This allows the agent to retrieve previous replies that are semantically similar to a new incoming message.

### What I built

```text
WhatsApp Export
      ↓
Clean Conversation Pairs
      ↓
Relationship Mapping
      ↓
Sentence Transformer
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Similarity Retrieval
```

### Relationship-specific memory

The retrieval system keeps conversation history separated by relationship:

* `history_family`
* `history_friend`
* `history_professional`
* `history_unknown`

Current dataset:

| Relationship |  Pairs |
| ------------ | -----: |
| Family       |     18 |
| Friend       |     14 |
| Professional |      0 |
| Unknown      |      0 |
| **Total**    | **32** |

The empty professional and unknown collections are expected because the current historical dataset only contains family and friend conversations.

### Important commands

Create and activate the Week 2 environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Check the active Python:

```powershell
where.exe python
```

Install dependencies:

```powershell
python -m pip install "chromadb[server]" sentence-transformers
```

Verify ChromaDB:

```powershell
python -m pip show chromadb
```

Start ChromaDB:

```powershell
chroma run --path .\chroma_data --port 8000
```

Validate the relationship map:

```powershell
python ingestion\validate_relationship_map.py
```

Verify sentence-transformers:

```powershell
python -c "import sklearn; from sentence_transformers import SentenceTransformer; print('sentence-transformers OK')"
```

Create embeddings and populate ChromaDB:

```powershell
python ingestion\embed_to_chroma.py
```

Test retrieval:

```powershell
python ingestion\retrieval_demo.py
```

Save retrieval results:

```powershell
$env:PYTHONIOENCODING="utf-8"
python ingestion\retrieval_demo.py | Tee-Object retrieval_results.txt
```

### Verification

The relationship map validation returned:

```text
Conversation IDs found: 2
Mapped IDs: 2

✅ Relationship map looks good
```

The embedding process successfully processed:

```text
Total input pairs: 32
Total processed: 32
```

The retrieval tests returned correctly ordered results and passed the distance sanity checks:

```text
✅ Distance sanity check: results are ordered correctly.
```

An exact historical message produced a distance of `0.000`, confirming that the vector retrieval was functioning correctly.

### Week 2 outcome

**Week 2 completed successfully.**

The project now has a working **History Brain** that can retrieve relevant historical conversation examples. In the next stage, this history retrieval will be combined with the **Persona Brain** from Week 1 to generate replies in my own communication style.
