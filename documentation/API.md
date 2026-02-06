# API Documentation

## ThalosApp Class

Main application controller.

### Constructor

```python
ThalosApp(gui_mode=True, crypto_mode=True)
```

**Parameters:**
- `gui_mode` (bool): Enable GUI interface
- `crypto_mode` (bool): Enable encryption

### Methods

#### query(txt, meta=None)
Process a query through the system.

**Parameters:**
- `txt` (str): Query text
- `meta` (dict): Optional metadata

**Returns:**
- dict: Response with answer, certainty, timestamp

**Example:**
```python
app = ThalosApp(gui_mode=False)
result = app.query("What is AI?")
print(result['answer'])
```

#### run_gui()
Launch GUI interface.

#### run_cli()
Run CLI interface loop.

#### report()
Print system statistics.

#### cleanup()
Release resources and shutdown.

## BioSynthesizer Class

SBI engine with 200M+ parameters.

### Constructor

```python
BioSynthesizer(param_goal=200000000)
```

### Methods

#### infer_query(txt, ctx=None)
Process query through neural wavefronts.

**Returns:**
- dict: Response with certainty score

## CognitionVault Class

Persistent memory system.

### Methods

#### archive_exchange(q, r, sess)
Store conversation.

#### recall_recent(count, sess=None)
Retrieve recent exchanges.

#### search_context(term, count)
Search by keyword.

## FusionConductor Class

Multi-modal data processing.

### Methods

#### conduct_fusion(data_bundle)
Fuse multiple modality inputs.

**Parameters:**
- `data_bundle`: Dict with 'text', 'numeric', 'metadata' keys

## CognitiveInferenceNet Class

Rule-based reasoning system.

### Methods

#### infer(query_txt, ctx_data=None)
Apply reasoning rules to query.

**Returns:**
- dict: Intent type, confidence, fired rules

## SecureVault Class

Encryption system.

### Methods

#### lock(data_obj)
Encrypt data.

#### unlock(enc_txt)
Decrypt data.

#### gen_token(ident)
Generate secure token.

## AsyncPool Class

Multi-threaded worker pool.

### Methods

#### dispatch(fn, *args, **kwargs)
Submit job for async execution.

**Returns:**
- str: Job ID

#### fetch_result(job_id, wait_time=None)
Get job result.

#### dispatch_many(job_list)
Submit multiple jobs.
