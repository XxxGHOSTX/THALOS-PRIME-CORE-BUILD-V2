# THALOS PRIME - Operations Runbook

This runbook provides operational procedures for running, monitoring, and maintaining THALOS PRIME.

## Table of Contents

1. [Installation](#installation)
2. [Starting the System](#starting-the-system)
3. [Monitoring & Telemetry](#monitoring--telemetry)
4. [Training & Optimization](#training--optimization)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)
7. [Security](#security)
8. [Backup & Recovery](#backup--recovery)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB+ RAM recommended
- 2GB+ disk space

### Quick Install

```bash
# Clone repository
git clone https://github.com/XxxGHOSTX/THALOS-PRIME-CORE-BUILD-V2.git
cd THALOS-PRIME-CORE-BUILD-V2

# Install dependencies
pip install -r dependencies.txt

# Or use quickstart
bash quickstart.sh

# Verify installation
python3 run_thalos.py --report
```

### Docker Install

```bash
# Build image
docker build -t thalos-prime .

# Run container
docker run -it thalos-prime
```

## Starting the System

### GUI Mode (Interactive)

```bash
python3 run_thalos.py --mode gui
```

**Requirements:** tkinter must be installed
**Features:** Floating window, particle effects, scrollable chat

### CLI Mode (Text-based)

```bash
python3 run_thalos.py --mode cli
```

**Usage:** Type queries and press Enter. Type `exit` to quit.

### Programmatic Usage

```python
from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault

# Initialize
bio = BioSynthesizer(200000000)  # 200M+ parameters
vault = CognitionVault("data.db")

# Run inference
result = bio.infer_query("Hello THALOS")

# Store in memory
vault.archive_exchange("Hello THALOS", result)
```

## Monitoring & Telemetry

### Real-time Dashboard

```python
from analytics_engine.telemetry_collector import TelemetryCollector
from analytics_engine.analytics_dashboard import AnalyticsDashboard

# Initialize
collector = TelemetryCollector()
dashboard = AnalyticsDashboard(collector)

# Record metrics
collector.record_metric('inference_latency', 100.5)
collector.record_metric('certainty', 0.85)

# Display dashboard
dashboard.display_dashboard()

# Export to JSON
json_data = dashboard.export_metrics(format='json')
```

### System Report

```bash
# Get full system report
python3 run_thalos.py --report
```

Output includes:
- Parameter count
- Memory statistics
- Worker pool status
- Session ID

### Metric Types

| Metric | Description | Target |
|--------|-------------|--------|
| `inference_latency` | Query processing time (ms) | < 200ms |
| `certainty` | Model confidence | > 0.7 |
| `memory_exchanges` | Stored exchanges | Monitor growth |
| `worker_utilization` | Thread pool usage | < 80% |

## Training & Optimization

### Train Model

```bash
# Synthetic data training
python3 synapse_matrix/scripts/train_codex.py \
  --epochs 10 \
  --batch-size 8 \
  --lr 0.001 \
  --num-samples 100

# Train from vault data
python3 synapse_matrix/scripts/train_codex.py \
  --data-source vault \
  --vault-path data.db \
  --epochs 10
```

### Benchmark Performance

```bash
# Run performance benchmark
python3 synapse_matrix/scripts/inference_codex.py \
  --mode benchmark \
  --benchmark-size 100

# Profile latency by query length
python3 synapse_matrix/scripts/inference_codex.py \
  --mode profile
```

### Predictive Optimization

```python
from predictive_engine.optimizer import PredictiveOptimizer
from analytics_engine.telemetry_collector import TelemetryCollector

# Initialize
collector = TelemetryCollector()
optimizer = PredictiveOptimizer(collector)

# Register parameters
optimizer.register_parameter('learning_rate', 0.001, 0.1, 0.01)

# Collect metrics
collector.record_metric('certainty', 0.75)

# Optimize
optimizations = optimizer.optimize_parameters(['certainty'])
```

## Troubleshooting

### Issue: High Latency

**Symptoms:** Inference takes > 500ms

**Solutions:**
1. Check parameter count: `bio.param_total` (lower if needed)
2. Monitor CPU/memory usage
3. Reduce context size
4. Check async worker pool

```python
# Check worker pool
pool = AsyncPool(4)
stats = pool.pool_stats()
print(f"Workers: {stats['alive']}/{stats['workers']}")
```

### Issue: Low Certainty Scores

**Symptoms:** `certainty < 0.5` consistently

**Solutions:**
1. Enable experimental mode
2. Increase training epochs
3. Check input quality
4. Review inference rules

```python
# Enable experimental mode
from experimental_mode.experimental_analyzer import ExperimentalAnalyzer

analyzer = ExperimentalAnalyzer()
analyzer.enable()

result = analyzer.analyze_query_experimental(query, context)
```

### Issue: Memory Growth

**Symptoms:** Database file growing too large

**Solutions:**
1. Clear old data: `vault.clear_old_data()`
2. Implement retention policy
3. Archive to external storage

```python
# Clear data older than 1 hour
vault.clear_old_data()  # Uses retention_seconds from init
```

### Issue: GUI Not Available

**Symptoms:** "GUI not available" message

**Solutions:**
1. Install tkinter: `sudo apt-get install python3-tk`
2. Use CLI mode instead
3. Use programmatic interface

## Maintenance

### Daily Tasks

- [ ] Check system report
- [ ] Monitor latency metrics
- [ ] Review error logs
- [ ] Verify worker health

```bash
# Daily check script
python3 run_thalos.py --report
python3 synapse_matrix/scripts/inference_codex.py --mode benchmark --benchmark-size 10
```

### Weekly Tasks

- [ ] Backup database
- [ ] Review training data quality
- [ ] Update telemetry dashboards
- [ ] Check disk usage

### Monthly Tasks

- [ ] Full system audit
- [ ] Performance tuning
- [ ] Update dependencies
- [ ] Review security settings

### Database Maintenance

```python
# Compact database
import sqlite3
conn = sqlite3.connect('data.db')
conn.execute('VACUUM')
conn.close()

# Get database size
import os
size_mb = os.path.getsize('data.db') / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")
```

## Security

### Encrypted Parameters

```python
from secure_params.crypto_vault import SecureVault

vault = SecureVault()

# Encrypt parameter
encrypted = vault.encrypt_param("sensitive_value")

# Decrypt parameter
decrypted = vault.decrypt_param(encrypted)
```

### Key Management

**Best Practices:**
1. Store encryption keys securely
2. Rotate keys regularly
3. Use environment variables
4. Never commit keys to git

```bash
# Set encryption key via environment
export THALOS_KEY="your-secure-key-here"
python3 run_thalos.py --mode cli
```

### Access Control

**Recommendations:**
1. Restrict file permissions: `chmod 600 data.db`
2. Use firewall rules if exposing API
3. Implement rate limiting
4. Log all access attempts

## Backup & Recovery

### Backup Database

```bash
# Manual backup
cp data.db data.db.backup.$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cp data.db "$BACKUP_DIR/data_$DATE.db"

# Keep last 30 days
find "$BACKUP_DIR" -name "data_*.db" -mtime +30 -delete
```

### Restore from Backup

```bash
# Stop system
# Replace database
cp data.db.backup.20260206 data.db

# Verify integrity
python3 -c "
from cognition_store.persistence import CognitionVault
vault = CognitionVault('data.db')
print(vault.vault_metrics())
"
```

### Snapshot System State

```python
from cognition_store.persistence import CognitionVault

vault = CognitionVault("data.db")

# Save system snapshot
state = {
    'bio_params': bio.param_total,
    'worker_count': 4,
    'config': {...}
}
vault.save_snapshot('system_state', state)

# Load snapshot
restored = vault.load_snapshot('system_state')
```

## Performance Tuning

### Optimization Checklist

- [ ] Tune parameter count for use case
- [ ] Adjust worker pool size
- [ ] Configure memory retention
- [ ] Enable predictive optimization
- [ ] Review inference rules
- [ ] Profile bottlenecks

### Parameter Tuning

```python
from predictive_engine.parameter_tuner import ParameterTuner

tuner = ParameterTuner()

# Start session
tuner.start_tuning_session('latency_opt', {
    'param_count': 200000000,
    'worker_count': 4
})

# Evaluate configurations
for config in configs:
    score = run_benchmark(config)
    tuner.evaluate_config(config, score)

# Get best config
best = tuner.get_best_config()
```

## Emergency Procedures

### System Unresponsive

1. Check process status: `ps aux | grep python`
2. Check resource usage: `top` or `htop`
3. Restart system: `Ctrl+C` then relaunch
4. Review logs for errors

### Data Corruption

1. Stop system immediately
2. Restore from latest backup
3. Run integrity checks
4. Review error logs
5. Contact support if needed

### Performance Degradation

1. Run benchmark to quantify
2. Check telemetry dashboard
3. Review recent changes
4. Rollback optimizations if needed
5. Clear caches and restart

## Support

For issues not covered in this runbook:

1. Check GitHub Issues: https://github.com/XxxGHOSTX/THALOS-PRIME-CORE-BUILD-V2/issues
2. Review documentation in `documentation/`
3. Run comprehensive tests: `python3 tests_comprehensive.py`
4. Create detailed bug report

---

*Last Updated: 2026-02-06*
*Version: 1.0*
