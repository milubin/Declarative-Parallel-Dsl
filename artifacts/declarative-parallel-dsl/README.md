# declarative-parallel-dsl + Agentic Workflows

Minimal declarative DSL for parallel programming — with autonomous agents, real Grok API integration, graph visualization, confidence-gated reflection loops, and persistent memory.

---

## API Key Safety

This project calls the [xAI Grok API](https://x.ai/api). You need your own API key to run examples 06, 07, and 08. Example 05 requires no API key.

**The API key is never stored in any Python file.** All code reads it exclusively from the environment variable `XAI_API_KEY` via `os.getenv("XAI_API_KEY")`. Never paste your key into source code or commit it to a repo.

### On Replit

1. Open the **Secrets** tab (🔒 icon in the left sidebar)
2. Click **New Secret**
3. Name: `XAI_API_KEY`
4. Value: your xAI API key (starts with `xai-`)
5. Click **Add Secret**

Replit injects it as an environment variable automatically — no `.env` file needed.

### Locally / after cloning from GitHub

Create a `.env` file in this directory (already listed in `.gitignore` — never commit it):

```bash
echo "XAI_API_KEY=xai-your-key-here" > .env
```

Then load it before running:

```bash
export $(cat .env) && python3 examples/06_agentic_grok_workflow.py
```

Or set it for the session:

```bash
export XAI_API_KEY=xai-your-key-here
python3 examples/06_agentic_grok_workflow.py
```

Get a key at: https://console.x.ai → sign in → **Create API Key**

---

## Architecture

```
Natural language command
        ↓
  GraphPlanner (networkx DiGraph)
        ↓
  Backend selection (CPU / GPU / Ray / CSL)
        ↓
  Parallel execution (agents or transforms)
        ↓
  Visualizer → saves graph PNG
        ↓
  Runtime rewrite if needed (Grok-like)
```

---

## Install

```bash
pip install -e .
pip install ray        # required for examples 07 and 08
```

---

## Examples

All commands run from `artifacts/declarative-parallel-dsl/`.

| File | What it shows | API key? | Ray? |
|------|---------------|----------|------|
| `01_simple_map.py` | CPU parallel map | No | No |
| `02_dataflow_pipeline.py` | Dataflow graph | No | No |
| `03_triton_gpu_kernel.py` | GPU kernel | No | CUDA GPU |
| `04_ray_distributed.py` | Distributed cluster | No | Yes |
| `05_agentic_workflow.py` | Autonomous agents + graph viz | No | No |
| `06_agentic_grok_workflow.py` | Real Grok API + Pride & Prejudice | Yes | No |
| `07_agentic_grok_ray_reflection.py` | Ray + Grok + reflection loops | Yes | Yes |
| `08_confidence_tools_memory.py` | Confidence-gated reflection + tools + memory | Yes | Yes |

---

## Quick Start

```bash
# Interactive agent (no API key needed)
python3 agent.py

# Agentic workflow with visualization (no API key needed)
python3 examples/05_agentic_workflow.py

# Real Grok API + large public text
python3 examples/06_agentic_grok_workflow.py

# Ray + Grok + self-critique reflection loops
python3 examples/07_agentic_grok_ray_reflection.py

# Confidence-gated workflow (stops early when agents are confident enough)
python3 examples/08_confidence_tools_memory.py

# Same, with results persisted to JSON + SQLite
python3 examples/08_confidence_tools_memory.py --debug
```

See [`instructions-agent-grok-ray.md`](instructions-agent-grok-ray.md) for a detailed walkthrough of each example.

---

## Agentic Workflow Pattern

```
Planner → [Researcher | Analyst | Critic | Historian] → Synthesizer
                          ↓ (reflection loop)
         [Researcher_Critic | Analyst_Critic | ...]
                          ↓
                    Synthesizer
```

Each agent runs in parallel via the DSL. Reflection loops let agents critique and improve their own outputs. Example 08 adds confidence scoring — agents self-rate 0.0–1.0 and loops stop automatically once average confidence crosses the threshold.

---

## Visualization

Each example saves a PNG graph of its agent workflow to `examples/`:

| Example | Graph file |
|---------|------------|
| 05 | `examples/agent_graph_cpu.png` |
| 06 | `examples/agent_graph_grok_cpu.png` |
| 07 | `examples/agent_graph_grok_ray.png` |
| 08 | `examples/agent_graph_confidence.png` |

---

## Backends

- **CPU** — ThreadPoolExecutor, always available
- **GPU** — Triton kernel, requires CUDA + `pip install torch triton`
- **Ray** — Distributed cluster, requires `pip install ray`
- **Cerebras CSL** — Generates CSL code skeletons for WSE-3

---

## Project Structure

```
declarative-parallel-dsl/
├── dsl/
│   ├── base_dsl.py          # Core ParallelDSL class, backend dispatch
│   ├── dataflow_dsl.py      # Dataflow graph DSL
│   ├── graph_planner.py     # networkx-based task graph planner
│   ├── visualizer.py        # matplotlib PNG graph renderer
│   └── backends/
│       ├── cpu_backend.py
│       ├── gpu_backend.py   # falls back to CPU if torch not installed
│       ├── ray_backend.py   # falls back to CPU if ray not installed
│       └── cerebras_csl.py  # stub / sketch
├── examples/
│   ├── 05_agentic_workflow.py
│   ├── 06_agentic_grok_workflow.py
│   ├── 07_agentic_grok_ray_reflection.py
│   └── 08_confidence_tools_memory.py
├── agent.py                 # natural-language CLI
├── instructions-agent-grok-ray.md
├── setup.py
└── README.md
```

---

## Security Notes

- `XAI_API_KEY` is read only from environment variables — never from files or code
- `.env` is listed in `.gitignore` to prevent accidental commits
- No credentials, tokens, or secrets appear anywhere in the source tree
- Ray CPU warnings are suppressed via env vars set in code, not via any secret
