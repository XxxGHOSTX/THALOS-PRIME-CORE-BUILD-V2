# THALOS PRIME User Guide

## Installation

1. Clone repository
2. Install dependencies: `pip install -r dependencies.txt`
3. Run tests: `python3 tests.py`

## Usage

### GUI Mode
- Launch: `python3 run_thalos.py --mode gui`
- Enter queries in text box
- Click "Process" or press Ctrl+Enter
- View responses and confidence scores

### CLI Mode
- Launch: `python3 run_thalos.py --mode cli`
- Type queries and press Enter
- Type 'exit' to quit

### Options
- `--mode gui|cli`: Choose interface
- `--no-crypto`: Disable encryption
- `--report`: Show system statistics

## Components

### SBI Engine
200M+ parameters for advanced reasoning

### Memory System
Stores all conversations in SQLite database

### Multi-Modal Fusion
Processes text, numbers, and metadata

### Confidence Scoring
Each response includes certainty metric

## Troubleshooting

**GUI won't start**: Install Tkinter or use CLI mode
**Memory errors**: Clear database with `rm data.db`
**Import errors**: Reinstall dependencies

## Examples

```python
# Greeting
You: Hello
THALOS: Greetings! THALOS PRIME operational...

# Question
You: What can you do?
THALOS: I provide advanced reasoning...

# Help
You: Help me
THALOS: I can assist with complex reasoning...
```
