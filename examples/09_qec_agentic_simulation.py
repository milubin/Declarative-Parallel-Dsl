"""
examples/09_qec_agentic_simulation.py

Agentic Quantum Error Correction (QEC) Simulation
  - 3-qubit bit-flip repetition code using Stim
  - 4 parallel simulation agents (varying noise levels) via Ray
  - Grok API analysis + reflection / critique round
  - Graph visualization  →  examples/agent_graph_qec.png
  - Results saved to     →  examples/qec_results.json  (always)

Requires:
  pip install stim ray
  XAI_API_KEY set in Replit Secrets

Run: python3 examples/09_qec_agentic_simulation.py
"""
import os
import logging
os.environ.setdefault("RAY_DISABLE_DOCKER_CPU_WARNING", "1")
os.environ.setdefault("RAY_ACCEL_ENV_VAR_OVERRIDE_ON_ZERO", "0")

import json
import re
import time
import ray
import numpy as np
import stim
import requests
from typing import List, Dict, Any
from openai import OpenAI

from dsl.base_dsl import ParallelDSL
from dsl.visualizer import visualize_graph
import networkx as nx

GROK_MODEL  = "grok-3"
DIVIDER     = "─" * 60
GRAPH_PATH  = "examples/agent_graph_qec.png"
RESULTS_PATH = "examples/qec_results.json"


# ── Grok client ───────────────────────────────────────────────────────────────

def create_grok_client() -> OpenAI:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError(
            "❌ XAI_API_KEY not set.\n"
            "   Replit: 🔒 Secrets tab → New Secret → XAI_API_KEY"
        )
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


# ── Core QEC simulation (Stim) ────────────────────────────────────────────────

def run_repetition_code(shots: int = 5000, noise: float = 0.01) -> Dict:
    """
    3-qubit bit-flip repetition code.
    Encodes |0_L> = |000>, applies depolarizing noise, measures all 3 qubits.
    Majority-vote decoder: logical error if 2 or more qubits flipped.
    Returns logical error rate and a sample of measurement outcomes.
    """
    circuit = stim.Circuit(f"""
        R 0 1 2
        DEPOLARIZE1({noise}) 0 1 2
        M 0 1 2
    """)
    sampler      = circuit.compile_sampler()
    measurements = sampler.sample(shots=shots)          # shape (shots, 3)

    # Majority-vote: logical error when ≥ 2 of 3 qubits measured as 1
    logical_errors = int(np.sum(np.sum(measurements, axis=1) >= 2))
    error_rate     = logical_errors / shots

    return {
        "shots":              shots,
        "noise":              noise,
        "logical_error_rate": round(error_rate, 6),
        "logical_errors":     logical_errors,
        "sample_outcomes":    measurements[:5].tolist(),
    }


# ── Ray remote agent ──────────────────────────────────────────────────────────

@ray.remote
def remote_qec_agent(
    agent_name: str,
    role: str,
    task: str,
    sim_params: Dict = None,
    prior_output: str = "",
) -> Dict[str, Any]:
    """
    Optionally runs a Stim simulation, then calls Grok for analysis.
    Returns JSON with analysis, confidence, and suggestions.
    """
    import os, time, json, re
    from openai import OpenAI
    import numpy as np
    import stim

    def run_sim(shots, noise):
        circuit = stim.Circuit(f"""
            R 0 1 2
            DEPOLARIZE1({noise}) 0 1 2
            M 0 1 2
        """)
        sampler      = circuit.compile_sampler()
        measurements = sampler.sample(shots=shots)
        errors       = int(np.sum(np.sum(measurements, axis=1) >= 2))
        return {
            "shots": shots, "noise": noise,
            "logical_error_rate": round(errors / shots, 6),
            "logical_errors": errors,
            "sample_outcomes": measurements[:5].tolist(),
        }

    client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
    start  = time.time()

    sim_result = run_sim(**sim_params) if sim_params else None
    sim_block  = f"\nSimulation result:\n{json.dumps(sim_result, indent=2)}\n" if sim_result else ""
    prior_block = (
        f"\nPrior analysis to improve upon:\n{prior_output[:2000]}\n"
        if prior_output else ""
    )

    prompt = f"""You are {role}.
Task: {task}
{sim_block}{prior_block}
Reply ONLY with valid JSON:
{{
  "analysis":    "<3-5 sentence scientific analysis>",
  "suggestions": ["<suggestion 1>", "<suggestion 2>"],
  "confidence":  <float 0.0-1.0>
}}"""

    resp = client.chat.completions.create(
        model="grok-3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=700,
    )
    raw   = resp.choices[0].message.content.strip()
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = {"analysis": raw, "suggestions": [], "confidence": 0.5}

    return {
        "agent":       agent_name,
        "role":        role,
        "simulation":  sim_result,
        "output":      parsed.get("analysis", raw),
        "suggestions": parsed.get("suggestions", []),
        "confidence":  float(parsed.get("confidence", 0.5)),
        "time":        round(time.time() - start, 2),
    }


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_qec_graph(agent_names: List[str], has_reflection: bool) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_node("Planner")
    G.add_node("Synthesizer")
    for name in agent_names:
        G.add_node(name)
        G.add_edge("Planner", name)
        if has_reflection:
            critic = f"{name}\n(Critic)"
            G.add_node(critic)
            G.add_edge(name, critic)
            G.add_edge(critic, "Synthesizer")
        else:
            G.add_edge(name, "Synthesizer")
    return G


def preview(text: str, chars: int = 120) -> str:
    return (text.replace("\n", " ").strip()[:chars] + "...") if len(text) > chars else text


# ── Main workflow ─────────────────────────────────────────────────────────────

def agentic_qec_workflow():
    # Noise sweep: 4 parallel agents, each at a different noise level
    param_sets = [
        {"shots": 5000, "noise": 0.005},
        {"shots": 5000, "noise": 0.010},
        {"shots": 5000, "noise": 0.020},
        {"shots": 5000, "noise": 0.040},
    ]
    agent_defs = [
        ("SimAgent_LowNoise",    "QEC Physicist — low noise regime"),
        ("SimAgent_BaseNoise",   "QEC Physicist — baseline noise"),
        ("SimAgent_HighNoise",   "QEC Physicist — high noise regime"),
        ("SimAgent_VeryHigh",    "QEC Physicist — very high noise regime"),
    ]

    # ── Step 1: Planner ───────────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("STEP 1 — Planner designs the experiment")
    print(DIVIDER)
    plan = ray.get(remote_qec_agent.remote(
        "Planner", "Quantum Experiment Designer",
        "Design a noise-sweep experiment for a 3-qubit bit-flip repetition code. "
        "Describe what we expect to see across four noise levels: 0.5%, 1%, 2%, 4%.",
    ))
    print(f"\n  [Planner] ✓ {plan['time']}s")
    print(f"  Analysis : {preview(plan['output'], 200)}")
    if plan["suggestions"]:
        for s in plan["suggestions"]:
            print(f"  • {s}")

    # ── Step 2: Local Stim preview ────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("STEP 2 — Local Stim sanity check before dispatching Ray agents")
    print(DIVIDER)
    for p in param_sets:
        r = run_repetition_code(**p)
        print(f"  noise={r['noise']:.3f}  →  logical_error_rate={r['logical_error_rate']:.4f}"
              f"  ({r['logical_errors']}/{r['shots']} shots)")

    # ── Step 3: Parallel Ray agents ───────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("STEP 3 — Parallel QEC simulation agents via Ray")
    print(DIVIDER)
    print("\n🚀 Dispatching 4 agents in parallel...\n")
    for (name, role), params in zip(agent_defs, param_sets):
        print(f"  ┌─ [{name}] {role}")
        print(f"  └─ noise={params['noise']}  shots={params['shots']:,} → Ray ✓")

    futures = [
        remote_qec_agent.remote(name, role, "Run the simulation and analyze the results.", params)
        for (name, role), params in zip(agent_defs, param_sets)
    ]
    results = ray.get(futures)

    print("\n  Results:")
    for r in results:
        sim = r["simulation"]
        flag = "✅" if r["confidence"] >= 0.8 else "🔄"
        print(f"\n  {flag} [{r['agent']}] noise={sim['noise']}  "
              f"error_rate={sim['logical_error_rate']:.4f}  "
              f"conf={r['confidence']:.2f}  ({r['time']}s)")
        print(f"     {r['output']}")
        if r["suggestions"]:
            for s in r["suggestions"]:
                print(f"     • {s}")

    # ── Step 4: Reflection / critique ─────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("STEP 4 — Reflection: agents critique each other's results")
    print(DIVIDER)
    print("\n🔄 Dispatching critic agents via Ray...\n")

    critique_futures = [
        remote_qec_agent.remote(
            f"{r['agent']}_Critic",
            "QEC Critic",
            f"Critique this analysis and suggest concrete improvements to the code or decoder:\n"
            f"noise={r['simulation']['noise']}  error_rate={r['simulation']['logical_error_rate']}",
            None,
            r["output"],
        )
        for r in results
    ]
    critiques = ray.get(critique_futures)

    print("  Critique results:")
    for c in critiques:
        print(f"\n  [{c['agent']}] conf={c['confidence']:.2f}  ({c['time']}s)")
        print(f"     {c['output']}")
        if c["suggestions"]:
            for s in c["suggestions"]:
                print(f"     • {s}")

    # ── Step 5: Graph ─────────────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print(f"STEP 5 — Building graph → {GRAPH_PATH}")
    print(DIVIDER)
    G = build_qec_graph([name for name, _ in agent_defs], has_reflection=True)
    visualize_graph(
        G,
        title="QEC Agentic Workflow — 3-Qubit Repetition Code (Stim + Ray + Grok)",
        output_path=GRAPH_PATH,
    )

    # ── Step 6: Synthesizer ───────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("STEP 6 — Synthesizer writes final report")
    print(DIVIDER)
    all_outputs = "\n\n---\n\n".join(
        f"[{r['agent']} | noise={r['simulation']['noise'] if r['simulation'] else 'n/a'} "
        f"| conf={r['confidence']:.2f}]\n{r['output']}"
        for r in results + critiques
    )
    final = ray.get(remote_qec_agent.remote(
        "Synthesizer", "QEC Final Report Writer",
        "Write a concise scientific report summarizing the noise-sweep experiment, "
        "key findings, and the most important recommendations for improving the repetition code.",
        None,
        all_outputs,
    ))
    print(f"  [Synthesizer] ✓ {final['time']}s")

    # ── Save results ──────────────────────────────────────────────────────────
    payload = {
        "plan":     plan,
        "results":  results,
        "critiques": critiques,
        "final":    final,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n  💾 Results saved → {RESULTS_PATH}")

    return payload


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ray.init(ignore_reinit_error=True, include_dashboard=False,
             object_store_memory=200 * 1024 * 1024,
             logging_level=logging.ERROR)

    print("=" * 60)
    print("🔬  Agentic QEC Simulation")
    print("    Stim · Ray · Grok API · Reflection loops")
    print("    3-Qubit Bit-Flip Repetition Code — Noise Sweep")
    print("=" * 60)

    total_start = time.time()
    result = agentic_qec_workflow()

    print(f"\n{'='*60}")
    print("📖  FINAL QEC REPORT")
    print("="*60)
    print(result["final"]["output"])
    if result["final"]["suggestions"]:
        print("\nKey recommendations:")
        for s in result["final"]["suggestions"]:
            print(f"  • {s}")
    print(f"\n⏱️  Total time  : {round(time.time()-total_start, 1)}s")
    print(f"Graph saved    : {GRAPH_PATH}")
    print(f"Results saved  : {RESULTS_PATH}")
    print("=" * 60)
