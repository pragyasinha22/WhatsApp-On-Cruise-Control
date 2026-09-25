# WEEK 2 — COMPLETE STEP-BY-STEP BUILD NOTES

## Building the WhatsApp "History Brain"

### Project

**Put Your WhatsApp on Cruise Control**

### Week 2 Goal

In Week 2, I built the **History Brain** of the project.

The goal was to take my WhatsApp chat history, clean it into useful conversation pairs, identify the relationship for each conversation, convert the messages into embeddings, store them in ChromaDB, and test whether the system could retrieve similar past conversations.

The basic flow was:

```text
WhatsApp Export
      ↓
Processed Conversation Pairs
      ↓
Relationship Mapping
      ↓
Embeddings
      ↓
ChromaDB
      ↓
Similarity Retrieval
```

---

# STEP 1 — Go to the Week 2 folder

My project is located at:

```text
C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control
```

I opened PowerShell and moved into the Week 2 folder.

### Command

```powershell
cd C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week2
```

### Why I used it

This makes `week2` the current working directory, so all the following commands operate on the Week 2 files.

---

# STEP 2 — Create the Week 2 Python virtual environment

I created a separate environment for Week 2.

### Command

```powershell
py -3.13 -m venv .venv
```

### What it does

Creates:

```text
week2/
└── .venv/
```

The `.venv` folder contains the isolated Python installation and packages for Week 2.

This prevents Week 2 dependencies from interfering with Week 1.

---

# STEP 3 — Activate the Week 2 environment

### Command

```powershell
.\.venv\Scripts\Activate.ps1
```

### What I checked

The PowerShell prompt should show:

```text
(.venv)
```

This means the virtual environment is active.

---

# STEP 4 — Check which Python is actually being used

This check became important because I initially discovered that my terminal was using the **Week 1 `.venv` instead of Week 2**.

### Command

```powershell
where.exe python
```

### What this command does

It shows all Python executables available through PATH.

I needed the first result to be:

```text
C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week2\.venv\Scripts\python.exe
```

Initially, it showed the Week 1 Python:

```text
C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week1\.venv\Scripts\python.exe
```

So I knew the wrong environment was active.

I deactivated/reactivated the environment and checked again.

After fixing it, the first result was:

```text
C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week2\.venv\Scripts\python.exe
```

### Why this check was important

If I installed ChromaDB into Week 2 but Python was still using Week 1, Python would say:

```text
ModuleNotFoundError: No module named 'chromadb'
```

even though I had installed it.

---

# STEP 5 — Install the Week 2 dependencies

I installed the packages needed for vector storage and embeddings.

### Command

```powershell
python -m pip install "chromadb[server]" sentence-transformers
```

### Why I installed them

### `chromadb`

Used as the vector database.

It stores the embeddings and allows similarity searches.

### `sentence-transformers`

Used to convert text into numerical vectors called **embeddings**.

Embeddings allow the system to search for messages with similar meaning.

### Installation note

I saw:

```text
WARNING: chromadb 1.5.9 does not provide the extra 'server'
```

This was not a fatal error.

The main `chromadb` package was installed successfully.

---

# STEP 6 — Verify that ChromaDB is installed

### Command

```powershell
python -m pip show chromadb
```

### What this checks

It checks whether the current Python environment has ChromaDB installed and shows its version/location.

I got:

```text
Name: chromadb
Version: 1.5.9
Location: C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week2\.venv\Lib\site-packages
```

### What this proved

ChromaDB was installed in the correct **Week 2 `.venv`**.

---

# STEP 7 — Prepare the Week 2 folders

The Week 2 structure used:

```text
week2/
├── data/
├── config/
├── ingestion/
└── ...
```

The important folders were:

```text
week2\data
week2\config
week2\ingestion
```

The `ingestion` folder contains the scripts responsible for preparing, embedding, and retrieving the historical data.

---

# STEP 8 — Create `data/processed_pairs.jsonl`

### File

```text
week2\data\processed_pairs.jsonl
```

This file contains the cleaned conversation pairs.

The important structure is:

```text
Their message → My reply
```

For example, one pair was:

```text
Their message:
Sunday ko ghar aaogi?

My reply:
Haan aa jaungi, Sunday free hoon ❤️
```

### Why I created this file

The incoming WhatsApp message will eventually become the search query.

The system needs historical examples showing:

```text
What they said
      ↓
How I replied
```

This gives the retrieval system useful examples of my previous responses.

---

# STEP 9 — Create the historical relationship map

### File

```text
week2\config\contact_relationship_map.json
```

This file maps each conversation to its relationship category.

The categories used were:

```text
family
friend
professional
unknown
```

### Why I created it

The agent should not search all WhatsApp history for every message.

For example:

```text
Family conversation
       ↓
family history only
```

and:

```text
Friend conversation
       ↓
friend history only
```

This makes the retrieval relationship-specific.

### Important distinction

This Week 2 map is based on the **historical conversation ID/name**.

It is not the same as the Week 3 live phone-number relationship map.

---

# STEP 10 — Create the relationship-map validation script

### File

```text
week2\ingestion\validate_relationship_map.py
```

I created this Python script to verify that the relationship map matched the conversation IDs found in the processed data.

### What the script checks

It checks things such as:

```text
Conversation IDs found
Mapped conversation IDs
Missing/unmapped IDs
```

The purpose is to catch mapping problems before embedding the data.

---

# STEP 11 — Run the relationship-map validation

### Command

```powershell
python ingestion\validate_relationship_map.py
```

### What this command does

It runs the validation script I created in the previous step.

### Result

```text
Conversation IDs found: 2
Mapped IDs: 2

✅ Relationship map looks good
```

### Meaning

The two conversation IDs found in my processed data were successfully mapped.

So the relationship mapping was ready for ingestion.

---

# STEP 12 — Verify sentence-transformers

Before running the embedding process, I checked that the embedding library could be imported.

### Command

```powershell
python -c "import sklearn; from sentence_transformers import SentenceTransformer; print('sentence-transformers OK')"
```

### What this checks

It verifies that:

* `sklearn` can be imported
* `sentence_transformers` can be imported
* the Week 2 Python environment has the required embedding dependencies

### Result

```text
sentence-transformers OK
```

This confirmed the embedding environment was working.

---

# STEP 13 — Start the ChromaDB server

I started a local ChromaDB server.

### Command

```powershell
chroma run --path .\chroma_data --port 8000
```

### What this does

It starts ChromaDB locally and stores its data under:

```text
week2\chroma_data
```

The server runs on:

```text
http://localhost:8000
```

### Result

The terminal showed:

```text
Saving data to: .\chroma_data
Connect to Chroma at: http://localhost:8000
Frontend server listening on address, addr: localhost:8000
```

### Important

I kept this terminal running because the ChromaDB server needs to remain available while the retrieval workflow uses it.

---

# STEP 14 — Create the embedding/ingestion script

### File

```text
week2\ingestion\embed_to_chroma.py
```

This is the main ingestion script.

### What this script does

It:

1. Loads the processed conversation pairs.
2. Loads the multilingual embedding model.
3. Reads the relationship mapping.
4. Separates data by relationship.
5. Converts `their_message` into embeddings.
6. Creates the appropriate ChromaDB collection.
7. Stores the embedding in ChromaDB.
8. Stores `my_reply` as metadata.

### Why embed `their_message`?

Because later, when a new WhatsApp message arrives, the incoming message is the query.

The system should search for historical messages similar to what the other person just sent.

So the retrieval structure is:

```text
New incoming message
        ↓
Search similar historical "their messages"
        ↓
Retrieve my historical reply
```

This is why the historical reply is stored as metadata associated with the embedded incoming message.

---

# STEP 15 — Run the embedding script

### Command

```powershell
python ingestion\embed_to_chroma.py
```

### What it does

This loads the embedding model and processes the historical conversation pairs into ChromaDB.

The model used was:

```text
paraphrase-multilingual-mpnet-base-v2
```

This was selected because the project may contain multilingual/Hinglish conversation data.

### Result

The script reported:

```text
Loading multilingual embedding model...
First run may download the model. Please wait.
```

Then:

```text
Embedding complete.
```

The final processing result was:

```text
Pairs processed by relationship:

history_family: 18
history_friend: 14
history_professional: 0
history_unknown: 0

Total input pairs: 32
Total processed: 32
```

### Final Week 2 data

```text
Family       = 18
Friend       = 14
Professional = 0
Unknown      = 0
Total        = 32
```

The professional and unknown collections had zero data because my current historical dataset did not contain those relationship types.

I did not create fake data just to fill those collections.

---

# STEP 16 — Understand the ChromaDB collections

The embedding script created relationship-specific collections:

```text
history_family
history_friend
history_professional
history_unknown
```

The actual data was:

```text
history_family
└── 18 historical pairs

history_friend
└── 14 historical pairs

history_professional
└── 0 pairs

history_unknown
└── 0 pairs
```

### Why separate collections?

The project should retrieve history from the appropriate relationship.

For example:

```text
Friend message
      ↓
history_friend
      ↓
Similar friend conversation
      ↓
My previous reply
```

This prevents unrelated family conversations from influencing a friend reply.

---

# STEP 17 — Create the retrieval demo

### File

```text
week2\ingestion\retrieval_demo.py
```

This script tests whether the historical data stored in ChromaDB can actually be retrieved.

### What the script does

It:

1. Takes a sample incoming message.
2. Determines the relationship collection.
3. Searches ChromaDB for similar historical messages.
4. Returns the closest historical examples.
5. Shows my previous reply.
6. Checks whether the results are correctly ordered by distance.

---

# STEP 18 — Run the retrieval demo

### Command

```powershell
python ingestion\retrieval_demo.py
```

### What this checks

This is the most important functional test of Week 2.

It checks whether:

```text
Query message
      ↓
Embedding
      ↓
ChromaDB search
      ↓
Similar historical message
      ↓
Historical reply
```

actually works.

---

# STEP 19 — Test family retrieval

One test query was:

```text
Babu khana kha liya?
```

The retrieval system searched the family history collection and returned relevant historical conversations.

Another test was:

```text
Sunday ko ghar aaogi?
```

The exact historical message was found.

The result included:

```text
Their message:
Sunday ko ghar aaogi?

My reply:
Haan aa jaungi, Sunday free hoon ❤️
```

The distance was:

```text
0.000
```

### What this means

The query exactly matched a stored historical message, so its distance was zero.

This was strong evidence that the retrieval system was working.

---

# STEP 20 — Test friend retrieval

I also tested friend-related messages.

Example:

```text
Movie ka plan hai kya?
```

The system searched:

```text
history_friend
```

and returned similar historical conversations.

Another test was:

```text
Yaar ye photo dekh 😂
```

The system returned a relevant historical conversation such as:

```text
Their message:
Okay 👍
Yaar ye photo dekh 😂

My reply:
Hahaha kya hai ye 😂😂
```

This demonstrated that the friend-specific retrieval was also working.

---

# STEP 21 — Check the retrieval distance ordering

The retrieval demo included a distance sanity check.

The output showed:

```text
✅ Distance sanity check: results are ordered correctly.
```

This appeared for the retrieval tests.

### Why I checked this

ChromaDB returns results based on similarity/distance.

The check confirms that the returned results are correctly ordered.

The most relevant result should appear before less relevant results.

---

# STEP 22 — Save the retrieval output

I wanted to keep a record of the retrieval tests.

### File created

```text
week2\retrieval_results.txt
```

### Command

```powershell
$env:PYTHONIOENCODING="utf-8"
python ingestion\retrieval_demo.py | Tee-Object retrieval_results.txt
```

### What this does

First:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

sets Python's console encoding to UTF-8.

This helps when displaying Unicode and emojis.

Then:

```powershell
python ingestion\retrieval_demo.py
```

runs the retrieval test again.

Finally:

```powershell
Tee-Object retrieval_results.txt
```

does two things:

1. Shows the output in the terminal.
2. Saves the same output into:

```text
retrieval_results.txt
```

---

# STEP 23 — Note about emoji display

In one Windows terminal output, some emojis appeared incorrectly, for example:

```text
Γ£à
≡ƒ...
```

This was a **Windows terminal encoding/display issue**.

It did not mean the WhatsApp data itself was corrupted.

The original successful retrieval output showed the emojis correctly, and the retrieval system itself worked.

---

# STEP 24 — Final Week 2 project structure

After completing the work, the important Week 2 structure was:

```text
week2/
│
├── .venv/
│
├── data/
│   └── processed_pairs.jsonl
│
├── config/
│   └── contact_relationship_map.json
│
├── ingestion/
│   ├── validate_relationship_map.py
│   ├── embed_to_chroma.py
│   └── retrieval_demo.py
│
├── chroma_data/
│
└── retrieval_results.txt
```

---

# STEP 25 — Commands I used and what each was for

## Move to Week 2

```powershell
cd C:\Users\psinh\Desktop\MasaiProjects\WhatsApp-On-Cruise-Control\week2
```

**Purpose:** Go to the Week 2 project directory.

---

## Create virtual environment

```powershell
py -3.13 -m venv .venv
```

**Purpose:** Create an isolated Python environment for Week 2.

---

## Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

**Purpose:** Activate the Week 2 Python environment.

---

## Check active Python

```powershell
where.exe python
```

**Purpose:** Confirm which Python executable is being used.

---

## Install dependencies

```powershell
python -m pip install "chromadb[server]" sentence-transformers
```

**Purpose:** Install ChromaDB and sentence-transformers.

---

## Check ChromaDB installation

```powershell
python -m pip show chromadb
```

**Purpose:** Verify ChromaDB version and installation location.

---

## Start ChromaDB

```powershell
chroma run --path .\chroma_data --port 8000
```

**Purpose:** Start the local ChromaDB server.

---

## Validate relationship map

```powershell
python ingestion\validate_relationship_map.py
```

**Purpose:** Check that all conversation IDs are correctly mapped to relationships.

---

## Check embedding library

```powershell
python -c "import sklearn; from sentence_transformers import SentenceTransformer; print('sentence-transformers OK')"
```

**Purpose:** Verify sentence-transformers and its dependency can be imported.

---

## Create embeddings and populate ChromaDB

```powershell
python ingestion\embed_to_chroma.py
```

**Purpose:** Convert historical messages into embeddings and store them in ChromaDB.

---

## Test retrieval

```powershell
python ingestion\retrieval_demo.py
```

**Purpose:** Check whether similar historical conversations and previous replies can be retrieved.

---

## Save retrieval results

```powershell
$env:PYTHONIOENCODING="utf-8"
python ingestion\retrieval_demo.py | Tee-Object retrieval_results.txt
```

**Purpose:** Run the retrieval test with UTF-8 console encoding and save the output to a text file.

---

# STEP 26 — Final Week 2 verification

## Data verification

```text
Total pairs = 32
Family = 18
Friend = 14
Professional = 0
Unknown = 0
```

## Relationship map verification

```text
Conversation IDs found: 2
Mapped IDs: 2

✅ Relationship map looks good
```

## Embedding verification

```text
sentence-transformers OK
```

## ChromaDB verification

ChromaDB was installed in:

```text
week2\.venv\Lib\site-packages
```

and the local server started successfully on:

```text
localhost:8000
```

## Embedding result

```text
Embedding complete.

Total input pairs: 32
Total processed: 32
```

## Retrieval verification

The retrieval demo successfully returned relevant historical conversations.

The distance checks showed:

```text
✅ Distance sanity check: results are ordered correctly.
```

An exact historical message returned:

```text
Distance: 0.000
```

---

# STEP 27 — What I completed in Week 2

* [x] Created a separate Week 2 virtual environment
* [x] Activated the environment
* [x] Verified the correct Python executable
* [x] Installed ChromaDB
* [x] Installed sentence-transformers
* [x] Verified ChromaDB installation
* [x] Started the ChromaDB server
* [x] Created/used processed conversation pairs
* [x] Created the historical relationship map
* [x] Created the relationship-map validation script
* [x] Validated the relationship map
* [x] Created the embedding ingestion script
* [x] Loaded the multilingual embedding model
* [x] Created relationship-specific ChromaDB collections
* [x] Embedded all 32 conversation pairs
* [x] Created the retrieval demo
* [x] Tested family retrieval
* [x] Tested friend retrieval
* [x] Checked retrieval distance ordering
* [x] Verified an exact match with distance `0.000`
* [x] Saved retrieval output to `retrieval_results.txt`

---

# FINAL RESULT

**Week 2 is complete.**

I successfully built the project's **History Brain**.

The History Brain can take an incoming message, search the appropriate relationship-specific ChromaDB collection, find similar historical messages, and return the way I replied to those messages in the past.

The Week 1 **Persona Brain** describes how I communicate.

The Week 2 **History Brain** provides relevant examples from my actual conversation history.

Together, these will later be used by the generation system to produce replies that are both **relevant to the conversation** and **consistent with my personal communication style**.

---

# Important Lesson From Week 2

The main idea I learned is:

> Instead of giving the AI my entire WhatsApp history every time, I can convert the history into searchable embeddings and retrieve only the relevant past conversations.

This makes the historical memory more targeted and useful for the later WhatsApp reply pipeline.
