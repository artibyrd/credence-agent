---
name: mesh-cluster
description: Launch, monitor, and test the 13-node Watts-Strogatz local P2P mesh cluster, Byzantine Sybil cartel resistance (3f+1), Barbell netsplits, and multi-hop gossip diffusion.
---

# 13-Node P2P Mesh Cluster Orchestration Skill

Use this skill when orchestrating or testing the decentralized P2P mesh network topology.

## Core Commands
- `just mesh-cluster-up`: Launch 13-node cluster with `hardware_guard.py` memory pre-flight.
- `just test -k mesh_cluster`: Execute hermetic cluster tests in pytest.
- `credence mesh --port 8765 --seed wss://relay.credence.nexus:8765`: Start an interactive relay node.

## Network Topology Invariants
- **Topology**: Watts-Strogatz small-world lattice ($N = 13$, degree $d = 4$, rewiring $\beta = 0.20$).
- **Byzantine Resilience**: $N \ge 3f + 1$ ($N = 13, f = 4$) cartels isolated.
- **Resource Constraints**: Hard `mem_limit: 128m` Docker cgroups per container; hardware guard throttles on $<2\text{GB}$ RAM hosts.
- **Pathological Scenarios**: Linear Daisy Chain TTL exhaustion, Barbell Netsplit partition recovery, Sybil Eclipse attack isolation, and Star topology flood control.

## Concurrent Swarm Testing Best Practices
- **Session Isolation**: When executing concurrent node tasks (`asyncio.gather(*tasks)`), always provision independent `AsyncSession` instances per node using `async_sessionmaker(bind=engine)` to prevent session flush race conditions.
- **Rendezvous Verification**: Verify that concurrent swarm nodes prioritize distinct feeds by asserting non-overlapping feed polling sequences across heterogeneous node pubkeys (`compute_feed_affinity(node_pubkey, feed_url)`).
- **P2P Cross-Adoption**: Verify that newly audited articles in node bursts are gossiped via `MeshGossipRelay.broadcast_attestation` and adopted by peer nodes at $0.00 token cost via `check_mesh_effort_avoidance`.
