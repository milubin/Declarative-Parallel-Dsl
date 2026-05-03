# declarative-parallel-dsl + Agentic Workflows

Minimal declarative DSL for parallel programming — now with autonomous agents, real Grok API integration, graph visualization, and self-critique (reflection) loops.

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

## Examples

| File | What it shows | Needs |
|---|---|---|
| `01_simple_map.py` | CPU parallel map | Nothing |
| `02_dataflow_pipeline.py` | Dataflow graph | Nothing |
| `03_triton_gpu_kernel.py` | GPU kernel | CUDA GPU |
| `04_ray_distributed.py` | Distributed cluster | Ray |
| `05_agentic_workflow.py` | Autonomous agents + graph viz | Nothing |
| `06_agentic_grok_workflow.py` | Real Grok API + Pride & Prejudice | `XAI_API_KEY` |
| `07_agentic_grok_ray_reflection.py` | Ray + Grok + reflection loops | `XAI_API_KEY` + Ray |

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Interactive agent (no API key needed)
python agent.py

# Agentic workflow with visualization (no API key needed)
python examples/05_agentic_workflow.py

# Real Grok API + large public text
python examples/06_agentic_grok_workflow.py

# Ray + Grok + self-critique reflection loops
python examples/07_agentic_grok_ray_reflection.py
```

## First-Time Grok API Setup

1. Go to [console.x.ai](https://console.x.ai) → sign in → **Create API Key**
2. In Replit: click the **🔒 Secrets** tab in the left sidebar
3. Add a new secret: key = `XAI_API_KEY`, value = your key
4. Run `python examples/06_agentic_grok_workflow.py`

## Agentic Workflow Pattern

```
Planner → [Researcher | Analyst | Critic | Historian] → Synthesizer
                                ↓ (reflection loop)
               [Researcher_Critic | Analyst_Critic | ...]
                                ↓
                          Synthesizer
```

Each agent runs in parallel via the DSL. Reflection loops let agents critique and improve each other's outputs. Graph is visualized and saved as a PNG.

## Backends

- **CPU** — ThreadPoolExecutor, always available
- **GPU** — Triton kernel, requires CUDA + `pip install torch triton`
- **Ray** — Distributed cluster, requires `pip install ray[default]`
- **Cerebras CSL** — Generates CSL code skeletons for WSE-3

## Future Cerebras CSL Backend

The `CerebrasCSLBackend` generates valid `layout.csl` + `pe_program.csl` skeletons. With the Cerebras SDK it would compile and run directly on WSE-3 (training and inference).

Happy teaching & hacking!
