# THALOS PRIME - Docker Deployment

## Build Image

```bash
docker build -t thalos-prime .
```

## Run Container

### CLI Mode
```bash
docker run -it thalos-prime
```

### With Volume (Persistent Memory)
```bash
docker run -it -v $(pwd)/data:/app thalos-prime
```

### System Report
```bash
docker run thalos-prime python3 run_thalos.py --report
```

## Environment Variables

No environment variables required for basic operation.

## Ports

No ports exposed (standalone chatbot application).

## Notes

- GUI mode requires X11 forwarding
- Default mode is CLI for container compatibility
- Memory stored in `/app/data.db` inside container
