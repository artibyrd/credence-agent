---
name: mesh-cluster
description: Dynamic P2P mesh peering (N >= 1, f = floor((N-1)/3)), local 13-node Watts-Strogatz benchmark testing, Byzantine Sybil cartel isolation (3f+1), and playground chaos simulation.
---

# P2P Mesh Cluster & Peering Orchestration Skill

Use this skill when orchestrating, monitoring, or testing the decentralized P2P mesh network topology.

## Architectural Boundary
- **Live Production Telemetry**: Reflects actual dynamic nodes ($N \ge 1$) from `PeerMetricRecord` and local node identity. When $N=1$, operates in `STANDALONE` mode ($f=0$). Byzantine quorum activates dynamically when $N \ge 4$ ($f = \lfloor (N-1)/3 \rfloor$). Never expose mock data or simulation buttons on production consoles.
- **Chaos Playground (`playground.md`)**: Dedicated 5-scenario 13-node Watts-Strogatz chaos simulation engine (Normal, Barbell Split, 3f+1 Sybil Eclipse, Genesis Seed Failover, Epidemic Burst) for interactive exploration and training.
- **Local Test Benchmark**: Canonical 13-node Watts-Strogatz lattice ($N=13, d=4, \beta=0.20, f=4$) used for hermetic pytest execution (`test_mesh_cluster.py`).

## Core Commands
- `just mesh-cluster-up`: Launch 13-node cluster with `hardware_guard.py` memory pre-flight.
- `just test -k mesh_cluster`: Execute hermetic cluster tests in pytest.
- `credence mesh --port 8765 --seed wss://relay.credence.nexus:8765`: Start an interactive relay node.
- `credence stats --mesh`: Inspect live swarm peering health and dynamic Byzantine quorum state.

## Network Topology Invariants
- **Benchmark Topology**: Watts-Strogatz small-world lattice ($N = 13$, degree $d = 4$, rewiring $\beta = 0.20$).
- **Byzantine Resilience**: $N \ge 3f + 1$ ($N = 13, f = 4$) cartels isolated.
- **Resource Constraints**: Hard `mem_limit: 128m` Docker cgroups per container; hardware guard throttles on $<2\text{GB}$ RAM hosts.
- **Pathological Scenarios**: Linear Daisy Chain TTL exhaustion, Barbell Netsplit partition recovery, Sybil Eclipse attack isolation, and Star topology flood control.

## Concurrent Swarm Testing Best Practices
- **Session Isolation**: When executing concurrent node tasks (`asyncio.gather(*tasks)`), always provision independent `AsyncSession` instances per node using `async_sessionmaker(bind=engine)` to prevent session flush race conditions.
- **Rendezvous Verification**: Verify that concurrent swarm nodes prioritize distinct feeds by asserting non-overlapping feed polling sequences across heterogeneous node pubkeys (`compute_feed_affinity(node_pubkey, feed_url)`).
- **P2P Cross-Adoption**: Verify that newly audited articles in node bursts are gossiped via `MeshGossipRelay.broadcast_attestation` and adopted by peer nodes at $0.00 token cost via `check_mesh_effort_avoidance`.

