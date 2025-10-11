# OBCMS Performance Testing Overview

## Objectives
- Define the full spectrum of performance validation required to protect OBCMS service-level targets across API, HTMX, Celery, and reporting workloads.
- Map each test category to the platform modules, environments, datasets, and observability tooling that underpin reliable execution.
- Provide actionable guidance framed by priority, complexity, dependencies, and prerequisites—never by calendar-based estimates.
- Establish governance for how findings are triaged, documented, and fed into remediation backlogs.

## Performance Targets & Service-Level Indicators
- **API Latency:** P95 < 800ms for authenticated requests hitting communities, coordination, monitoring, and policies endpoints.
- **HTMX Interactions:** User-visible swaps complete < 1.2s P95 with graceful fallback messaging on failure.
- **Background Jobs:** Celery task completion < 2 minutes P95 for WorkItem escalations, notifications, and recommendation batching.
- **Throughput:** Sustain ≥ 300 concurrent active users without exceeding 70% CPU utilization or 75% database connection pool usage.
- **Error Budgets:** Maintain < 0.5% 5xx error rate across services; < 1% HTMX partial failure notifications.
- **Data Freshness:** Analytics dashboards refresh within 5 minutes of upstream data changes under sustained load.

## Environment & Dataset Matrix
| Scope | Priority | Complexity | Target Environment | Dependencies | Prerequisites |
| --- | --- | --- | --- | --- | --- |
| Baseline verification | CRITICAL | Simple | CI ephemeral container | pytest suite, smoke fixtures | Synthetic seed data, feature flags aligned with staging |
| Sustained load & soak | CRITICAL | Complex | Staging (production parity) | k6 runners, Grafana dashboards | Sanitized production snapshot, dedicated monitoring stack |
| Chaos & resilience | HIGH | Complex | Staging canary or isolated chaos env | Chaos tooling, failover scripts | Runbooks for recovery, feature toggle support |
| Capacity & scalability | MEDIUM | Complex | Infrastructure lab / auto-scaling sandbox | IaC scripts, load balancer config | Cost approvals, observability on replicas |

## Test Categories

### Load Testing
- **Priority:** CRITICAL
- **Complexity:** Moderate
- **Dependencies:** Core API endpoints, HTMX interaction surfaces, baseline infrastructure sizing.
- **Prerequisites:** Stable staging environment, k6 baseline scripts, seeded database with representative data volume.
- **Purpose:** Validate that average and peak usage can be handled without breaching latency SLAs or exceeding CPU/memory budgets.
- **Implementation Notes:** Execute with k6 (`constant-vus`, `ramping-vus`) and complement with Locust for live user behavior modeling when needed. Prioritize high-traffic modules including communities directories, coordination kanban, monitoring dashboards, recommendations management, and executive analytics APIs.

### Stress Testing
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Autoscaling policies, rate-limiting middleware, cache configuration.
- **Prerequisites:** Observability stack in place (Grafana, Prometheus/InfluxDB), alert thresholds defined.
- **Purpose:** Identify the breaking point of services and confirm graceful degradation under extreme but short-lived surges.
- **Implementation Notes:** Extend k6 scripts with `ramping-arrival-rate` to push beyond expected concurrency; capture recovery time, saturation metrics, and error growth.

### Spike Testing
- **Priority:** HIGH
- **Complexity:** Moderate
- **Dependencies:** Queue consumers, HTMX partial endpoints, authentication layer.
- **Prerequisites:** Ability to replay real spike scenarios (e.g., mass policy updates, advisory broadcasts).
- **Purpose:** Ensure OBCMS can absorb sudden bursts triggered by emergency coordination or broadcast events without cascading failures.
- **Implementation Notes:** Use k6 scenarios with abrupt VU jumps; pair with synthetic Celery task injection to mirror downstream load—particularly for WorkItem escalations, recommendations approvals, and rapid dashboard refreshes.

### Soak / Endurance Testing
- **Priority:** HIGH
- **Complexity:** Complex
- **Dependencies:** Background jobs, scheduled tasks, database connection pooling, cache eviction rules.
- **Prerequisites:** Long-running staging environment with monitoring for resource drift, log rotation policies.
- **Purpose:** Detect memory leaks, slow resource exhaustion, or data integrity drift during prolonged activity windows.
- **Implementation Notes:** Run k6 for sustained endurance windows using `constant-arrival-rate`; monitor DB connections, Celery worker heartbeat, cache hit ratios, and WebSocket subscription stability.

### Volume / Data Growth Testing
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Data imports (`data_imports`), reporting queries, storage tier.
- **Prerequisites:** High-volume fixture generation scripts, isolated database snapshot.
- **Purpose:** Validate performance of data-heavy operations (bulk imports, complex reports) as records approach projected maxima.
- **Implementation Notes:** Combine batch scripts with targeted k6 or CLI tools; analyze query plans and storage growth across monitoring WorkItems, recommendations archives, planning scenarios, and M&E indicators.

### Scalability Testing
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Horizontal scaling topology (app servers, Celery workers), database replicas, load balancer configuration.
- **Prerequisites:** Infrastructure-as-code or deployment scripts capable of adding/removing nodes on demand.
- **Purpose:** Measure performance changes when scaling resources up or down, ensuring linear or near-linear throughput gains.
- **Implementation Notes:** Coordinate with infrastructure team; use k6 distributed execution or cloud-based runners to maintain sustained load while varying resources. Track cost/performance ratios for decision making.

### Capacity Testing
- **Priority:** MEDIUM
- **Complexity:** Moderate
- **Dependencies:** Aggregate resource budgets (CPU, memory, IOPS), service limits from cloud providers.
- **Prerequisites:** Resource dashboards with utilization metrics, cost and quota documentation.
- **Purpose:** Determine maximum concurrent users and operations supported by the current footprint before SLA breaches occur.
- **Implementation Notes:** Start from load-test baselines; increment concurrency until thresholds fail; record resource headroom for planning, especially for calendar-heavy monitoring operations and analytics dashboards.

### Resilience / Chaos Testing
- **Priority:** MEDIUM
- **Complexity:** Complex
- **Dependencies:** Fallback mechanisms, retry logic, failover databases, message queues.
- **Prerequisites:** Chaos tooling (e.g., Chaos Mesh, Gremlin) or scripted failure injection, incident response runbooks.
- **Purpose:** Validate service stability when dependencies fail (DB outage, cache flush, network latency spikes) and confirm user-facing impact stays acceptable.
- **Implementation Notes:** Pair failure injection with active load tests; monitor HTMX error banners, API error rates, Celery retry counts, and recovery workflows.

## Data Management & Seeding Guidelines
- Maintain anonymized production snapshots refreshed on the approved data-refresh cadence; scrub PII and sensitive government identifiers before import.
- Provide dataset-specific seeding scripts under `data_imports/` with markers for high-volume tables (communities, WorkItems, beneficiaries, policy records).
- Ensure fixture builders create realistic relational depth: multi-level administrative regions, recurring calendar entries, recommendation feedback loops.
- Version seed datasets and document schema compatibility to prevent drift between releases.

## Observability & Instrumentation
- Leverage OpenTelemetry exporters already configured in `obc_management` to capture traces for API endpoints and Celery tasks.
- Emit business KPIs (WorkItem escalation time, recommendation acceptance) via StatsD/Prometheus metrics for correlation during tests.
- Configure Grafana dashboards with dedicated panels for latency percentiles, error budgets, queue depth, cache hit ratios, and DB connection pools.
- Enable application-level logging at INFO for baseline tests and DEBUG for targeted diagnostics; aggregate logs in Loki or ELK.

## Tooling & Automation
- Primary load tool: k6 (see [k6 Load Testing Plan](obcms_k6_load_testing_plan.md)).
- Supplemental tools:
  - Locust for user-behavior scripting.
  - Apache JMeter for complex multipart or SOAP legacy integrations.
  - Chaos tooling (Chaos Mesh, Gremlin) for resilience experiments.
  - pgbadger / pg_stat_statements for deep database analysis during volume tests.
- Results aggregation: Grafana dashboards fed by Prometheus/InfluxDB exporters, CI artifacts stored under `reports/performance/`.
- Automate baseline load tests via CI pipelines triggered on release branch merges; publish summary metrics alongside pytest results.

## Execution Workflow
1. **Plan** — Select target test category, confirm dependencies, obtain approvals for environment usage, and align monitoring dashboards.
2. **Prepare** — Refresh datasets, update k6/Locust scripts, configure feature toggles, and validate observability endpoints.
3. **Execute** — Run scenarios, capture metrics and logs, and annotate anomalies in real time.
4. **Analyze** — Compare results against service-level indicators, document regressions, and assign owners.
5. **Remediate** — File issues in the backlog with reproduction steps, attach dashboards or trace IDs, and track follow-up fixes.
6. **Report** — Store findings in `reports/performance/` with summary, impacted modules, and remediation commitments.

## Governance & Responsibilities
- **Performance Champion (QA Lead):** Owns test schedule, approves scripts, ensures documentation alignment.
- **DevOps Engineer:** Maintains k6 infrastructure, autoscaling policies, and monitoring integrations.
- **Feature Teams:** Supply representative workloads, review results, and implement remediation tasks.
- **Incident Commander:** Evaluates chaos testing outcomes and updates incident response playbooks.
- Rotate ownership on a fixed cadence to distribute knowledge across engineering teams without slipping into calendar-driven commitments.

## Risk Register & Mitigation
- **Risk:** Insufficient dataset realism causes false positives/negatives.
  - **Mitigation:** Validate fixtures against production analytics; incorporate stakeholder feedback on peak patterns.
- **Risk:** Chaos experiments impact shared staging resources.
  - **Mitigation:** Use feature flags and canary environments; communicate windows in advance.
- **Risk:** Observability gaps hide regressions.
  - **Mitigation:** Enforce tracing coverage and alert on metric silence as well as spikes.
- **Risk:** Performance regressions reach production unnoticed.
  - **Mitigation:** Gate releases on load test sign-off and integrate metrics into deployment checklists.

## Process Integration
- Schedule high-priority categories (load, stress, soak) on recurring cadences aligned with release trains.
- Trigger medium-priority categories before major infrastructure or module rollouts.
- Capture findings in `reports/performance/` with remediation tasks filed in the issue tracker.
- Update test plans when new modules launch or infrastructure changes modify dependencies.

## Next Steps
- **Priority:** HIGH — Finalize tooling stack and automate load/stress scenarios in CI.
- **Priority:** HIGH — Define soak-test cadence and monitoring alerts for resource drift.
- **Priority:** MEDIUM — Stand up chaos testing workflow tied to staging or canary environments.
- **Priority:** MEDIUM — Document data volume fixture generation scripts for volume and scalability exercises.
- **Priority:** MEDIUM — Implement dashboards tracking error budgets and latency objectives referenced above.
