# declarative-parallel-dsl

Minimal, student-friendly declarative DSL for parallel programming.  
Say *what* you want (map, pipeline, dataflow graph) — the runtime hides threads, GPU kernels, distributed actors, or even future Cerebras CSL dataflow.

Inspired by `std::execution::par`, TBB Flow Graph, NVIDIA stdexec, and Cerebras-style dataflow.

## Features
- Same clean API across CPU, Triton GPU, Ray (distributed cluster), and a CSL sketch for Cerebras WSE
- Zero-boilerplate for students
- Easy to extend

## Install
```bash
pip install -e .
```

## Quick Examples
```bash
python examples/01_simple_map.py          # CPU parallel map
python examples/02_dataflow_pipeline.py   # dataflow graph
python examples/03_triton_gpu_kernel.py   # GPU (requires CUDA)
python examples/04_ray_distributed.py     # multi-node / cluster
```

## Future Cerebras CSL Backend
The `CerebrasCSLBackend` already generates valid layout + PE code skeletons. When you have access to the Cerebras SDK it will compile and run directly on WSE-3 (both training and inference).

Happy teaching & hacking!
