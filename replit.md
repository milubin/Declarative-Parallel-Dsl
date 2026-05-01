# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## Projects

### declarative-parallel-dsl (`artifacts/declarative-parallel-dsl/`)
Python 3.12 project. Minimal declarative DSL for parallel programming with four backends:
- **CPU** (`dsl/backends/cpu.py`) — ThreadPoolExecutor, works everywhere
- **GPU** (`dsl/backends/triton_gpu.py`) — Triton kernel, requires CUDA
- **Ray** (`dsl/backends/ray_distributed.py`) — distributed cluster via Ray
- **Cerebras CSL** (`dsl/backends/cerebras_csl.py`) — generates layout.csl + pe_program.csl for WSE-3

Run: `cd artifacts/declarative-parallel-dsl && python3 examples/01_simple_map.py`
Test: `cd artifacts/declarative-parallel-dsl && python3 tests/test_dsl.py`
Install (editable): `cd artifacts/declarative-parallel-dsl && pip install -e .`
