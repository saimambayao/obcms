# Query Template System Implementation Checklist

**Project**: OBCMS Query Template System Expansion
**Goal**: Scale from 151 to 575 templates
**Timeline**: 8 weeks (4 phases)
**Status**: Architecture Complete | Ready for Implementation

---

## Quick Status Overview

| Phase | Priority | Status | Templates | Duration |
|-------|----------|--------|-----------|----------|
| Phase 1: Foundation | CRITICAL | ⬜ Not Started | 0 → 0 | Weeks 1-2 |
| Phase 2: Core Enhancement | HIGH | ⬜ Not Started | 151 → 385 | Weeks 3-4 |
| Phase 3: New Domains | HIGH | ⬜ Not Started | 385 → 575 | Weeks 5-6 |
| Phase 4: Enhancement | MEDIUM | ⬜ Not Started | 575 (optimize) | Weeks 7-8 |

**Current**: 151 templates | **Target**: 575 templates | **Progress**: 26% complete

---

## Phase 1: Foundation (Weeks 1-2) | PRIORITY: CRITICAL

**Goal**: Build advanced registry infrastructure supporting 500+ templates with <10ms performance.

### 1.1 Advanced Registry Implementation ⬜

**Tasks**:
- [ ] Create `src/common/ai_services/chat/query_templates/registry/` directory
- [ ] Implement `advanced_registry.py` with AdvancedTemplateRegistry class
- [ ] Implement `template_loader.py` with LazyTemplateLoader class
- [ ] Add backward compatibility facade in `__init__.py`
- [ ] Update `get_template_registry()` to use advanced registry

**Deliverables**:
- ✅ AdvancedTemplateRegistry class with lazy loading
- ✅ LazyTemplateLoader with dynamic imports
- ✅ Backward compatibility maintained

**Success Criteria**:
- [ ] All existing tests pass (no breaking changes)
- [ ] Lazy loading reduces startup time by >70%
- [ ] Memory usage <15MB with lazy loading

**Files**:
- `registry/__init__.py`
- `registry/advanced_registry.py`
- `registry/template_loader.py`

---

### 1.2 Trie-Based Pattern Indexing ⬜

**Tasks**:
- [ ] Implement PatternTrie class in `advanced_registry.py`
- [ ] Add pattern prefix extraction logic
- [ ] Build trie index on template registration
- [ ] Update `find_matching_templates()` to use trie
- [ ] Add trie rebuild method for dynamic updates

**Deliverables**:
- ✅ PatternTrie class with insert/search methods
- ✅ Pattern prefix extraction
- ✅ Trie-optimized template matching

**Success Criteria**:
- [ ] Search space reduced by >80% (500 → ~50 candidates)
- [ ] Match time reduced by >60% (10ms → <4ms)
- [ ] Index build time <50ms (one-time cost)

**Performance Target**: <4ms average match time

---

### 1.3 Priority Queue Ranking ⬜

**Tasks**:
- [ ] Import heapq for priority queue operations
- [ ] Update `rank_templates()` to use heap-based top-k
- [ ] Add configurable top_k parameter (default: 10)
- [ ] Optimize heap operations for performance
- [ ] Add performance benchmarks

**Deliverables**:
- ✅ Heap-based ranking algorithm
- ✅ Configurable top-k results
- ✅ Performance benchmarks

**Success Criteria**:
- [ ] Ranking time reduced by >60% (15ms → <6ms)
- [ ] Memory usage: O(n) → O(k) where k=10
- [ ] Top-10 retrieval <5ms

---

### 1.4 Multi-Level Caching ⬜

**Tasks**:
- [ ] Implement L1 cache (in-memory LRU) using functools.lru_cache
- [ ] Implement L2 cache (Redis) using django.core.cache
- [ ] Add cache key generation logic
- [ ] Implement CachedTemplateRegistry class
- [ ] Add cache warming for high-priority categories
- [ ] Add cache invalidation on template updates

**Deliverables**:
- ✅ L1 cache: Pattern compilation (1000 entries)
- ✅ L2 cache: Template matches (Redis, 300s TTL)
- ✅ Cache warming strategy
- ✅ Invalidation logic

**Success Criteria**:
- [ ] Cache hit rate >75% after warm-up
- [ ] Cached match time <1ms (L1 hit)
- [ ] Effective match time <3ms (80% cache hit rate)

---

### 1.5 Performance Testing Framework ⬜

**Tasks**:
- [ ] Create `tests/test_query_templates/test_performance.py`
- [ ] Add benchmark tests for match time (<10ms)
- [ ] Add benchmark tests for lazy loading (<20ms)
- [ ] Add benchmark tests for full registry search (<50ms)
- [ ] Add memory usage benchmarks (<25MB)
- [ ] Add cache hit rate tests (>75%)
- [ ] Set up CI/CD performance regression detection

**Deliverables**:
- ✅ Performance test suite
- ✅ Benchmark fixtures
- ✅ CI/CD integration

**Success Criteria**:
- [ ] All performance tests pass
- [ ] Benchmarks integrated in CI/CD
- [ ] Performance regression detection active

**Files**:
- `tests/test_query_templates/test_performance.py`
- `.github/workflows/test-query-templates.yml`

---

### 1.6 Phase 1 Validation ⬜

**Tasks**:
- [ ] Run full test suite (`pytest tests/test_query_templates/ -v`)
- [ ] Run performance benchmarks (`pytest -m benchmark`)
- [ ] Verify backward compatibility (all existing code works)
- [ ] Measure startup time (target: <100ms)
- [ ] Measure memory usage (target: <20MB)
- [ ] Measure cache hit rate (target: >75%)

**Success Criteria**:
- [ ] ✅ All tests pass (100% pass rate)
- [ ] ✅ Performance targets met (<10ms match)
- [ ] ✅ No breaking changes
- [ ] ✅ Lazy loading reduces startup by >70%
- [ ] ✅ Cache hit rate >75%

**Phase 1 Complete**: ⬜ (Mark when all tasks done)

---

## Phase 2: Core Domain Enhancement (Weeks 3-4) | PRIORITY: HIGH

**Goal**: Reorganize existing 151 templates and add 234 new templates to core domains (total: 385).

### 2.1 Communities Domain Enhancement ⬜

**Current**: 25 templates | **Target**: 65 templates | **New**: 40

**Tasks**:
- [ ] Create `core_domains/communities/` directory
- [ ] Split into query type files:
  - [ ] `count_queries.py` (15 templates: 5 existing + 10 new)
  - [ ] `list_queries.py` (15 templates: 8 existing + 7 new)
  - [ ] `aggregate_queries.py` (10 templates: 2 existing + 8 new)
  - [ ] `demographic_queries.py` (15 templates: 5 existing + 10 new)
  - [ ] `location_queries.py` (10 templates: 5 existing + 5 new)
- [ ] Write unit tests for all 65 templates
- [ ] Generate documentation (`python manage.py generate_template_docs --category communities`)

**New Template Types**:
- Population statistics and demographics
- Historical community data
- Multi-criteria filters (ethnicity + livelihood + location)
- Community comparisons (Region IX vs Region X)
- Validation queries (missing data checks)

**Success Criteria**:
- [ ] All 65 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.2 Coordination Domain Enhancement ⬜

**Current**: 30 templates | **Target**: 75 templates | **New**: 45

**Tasks**:
- [ ] Create `core_domains/coordination/` directory
- [ ] Split into query type files:
  - [ ] `stakeholder_queries.py` (20 templates)
  - [ ] `partnership_queries.py` (20 templates)
  - [ ] `meeting_queries.py` (20 templates)
  - [ ] `organization_queries.py` (15 templates)
- [ ] Write unit tests for all 75 templates
- [ ] Generate documentation

**New Template Types**:
- Stakeholder engagement metrics
- Partnership effectiveness tracking
- Meeting attendance and outcomes
- Organization capacity assessments
- Cross-stakeholder coordination

**Success Criteria**:
- [ ] All 75 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.3 MANA Domain Enhancement ⬜

**Current**: 21 templates | **Target**: 60 templates | **New**: 39

**Tasks**:
- [ ] Create `core_domains/mana/` directory
- [ ] Split into query type files:
  - [ ] `workshop_queries.py` (20 templates)
  - [ ] `assessment_queries.py` (15 templates)
  - [ ] `needs_queries.py` (15 templates)
  - [ ] `facilitator_queries.py` (10 templates)
- [ ] Write unit tests for all 60 templates
- [ ] Generate documentation

**New Template Types**:
- Workshop completion and effectiveness
- Needs classification and analysis
- Facilitator performance tracking
- Assessment quality validation
- Temporal trends (workshops over time)

**Success Criteria**:
- [ ] All 60 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.4 Policies Domain Enhancement ⬜

**Current**: 25 templates | **Target**: 60 templates | **New**: 35

**Tasks**:
- [ ] Create `core_domains/policies/` directory
- [ ] Split into query type files:
  - [ ] `recommendation_queries.py` (20 templates)
  - [ ] `evidence_queries.py` (15 templates)
  - [ ] `tracking_queries.py` (15 templates)
  - [ ] `approval_queries.py` (10 templates)
- [ ] Write unit tests for all 60 templates
- [ ] Generate documentation

**Success Criteria**:
- [ ] All 60 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.5 Projects Domain Enhancement ⬜

**Current**: 25 templates | **Target**: 60 templates | **New**: 35

**Tasks**:
- [ ] Create `core_domains/projects/` directory
- [ ] Split into query type files:
  - [ ] `ppa_queries.py` (20 templates)
  - [ ] `budget_queries.py` (15 templates)
  - [ ] `monitoring_queries.py` (15 templates)
  - [ ] `reporting_queries.py` (10 templates)
- [ ] Write unit tests for all 60 templates
- [ ] Generate documentation

**Success Criteria**:
- [ ] All 60 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.6 Staff & General Domain Enhancement ⬜

**Current**: 25 templates | **Target**: 65 templates | **New**: 40

**Staff Domain** (10 → 35 templates):
- [ ] Create `core_domains/staff/` directory
- [ ] `task_queries.py` (15 templates)
- [ ] `user_queries.py` (10 templates)
- [ ] `permission_queries.py` (10 templates)

**General Domain** (15 → 30 templates):
- [ ] Create `core_domains/general/` directory
- [ ] `help_queries.py` (15 templates)
- [ ] `system_queries.py` (10 templates)
- [ ] `faq_queries.py` (5 templates)

**Success Criteria**:
- [ ] All 65 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 2.7 Phase 2 Validation ⬜

**Tasks**:
- [ ] Run full test suite (all 385 templates)
- [ ] Verify all templates registered successfully
- [ ] Check performance (still <10ms match time)
- [ ] Verify memory usage (<20MB)
- [ ] Generate all category documentation
- [ ] Run integration tests with test database

**Success Criteria**:
- [ ] ✅ All 385 templates registered (151 → 385)
- [ ] ✅ 100% test coverage maintained
- [ ] ✅ Performance <10ms maintained
- [ ] ✅ Memory usage <20MB
- [ ] ✅ Documentation complete

**Phase 2 Complete**: ⬜ (Mark when all tasks done)

---

## Phase 3: New Domain Addition (Weeks 5-6) | PRIORITY: HIGH

**Goal**: Add 8 new domain categories with 190 new templates (total: 575).

### 3.1 Geographic Domain (40 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/geographic/` directory
- [ ] `region_queries.py` (10 templates)
- [ ] `province_queries.py` (10 templates)
- [ ] `municipality_queries.py` (10 templates)
- [ ] `barangay_queries.py` (10 templates)
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "List all provinces in Region IX"
- "Count municipalities by province"
- "Show barangays with incomplete data"

---

### 3.2 Temporal Domain (30 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/temporal/` directory
- [ ] `date_range_queries.py` (10 templates)
- [ ] `trend_queries.py` (10 templates)
- [ ] `historical_queries.py` (10 templates)
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "Workshop trends last 6 months"
- "Communities added this year"
- "Historical partnership growth"

---

### 3.3 Cross-Domain Domain (30 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/cross_domain/` directory
- [ ] `community_mana_queries.py` (10 templates)
- [ ] `coordination_policy_queries.py` (10 templates)
- [ ] `project_community_queries.py` (10 templates)
- [ ] Implement CrossDomainQueryBuilder utility
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "How many MANA workshops for communities in Region IX?"
- "Policies related to active partnerships"
- "Projects benefiting Maranao communities"

**Critical**: Requires multi-model query generation

---

### 3.4 Analytics Domain (25 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/analytics/` directory
- [ ] `comparison_queries.py` (10 templates)
- [ ] `ranking_queries.py` (10 templates)
- [ ] `correlation_queries.py` (5 templates)
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "Compare Region IX vs Region X communities"
- "Top 10 communities by population"
- "Correlation between livelihood and population"

---

### 3.5 Reports Domain (20 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/reports/` directory
- [ ] `summary_queries.py` (10 templates)
- [ ] `dashboard_queries.py` (5 templates)
- [ ] `export_queries.py` (5 templates)
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "Generate community summary report"
- "Dashboard stats for this month"
- "Export communities to CSV"

---

### 3.6 Validation Domain (15 templates) ⬜

**Tasks**:
- [ ] Create `new_domains/validation/` directory
- [ ] `data_quality_queries.py` (10 templates)
- [ ] `completeness_queries.py` (5 templates)
- [ ] Write unit tests
- [ ] Generate documentation

**Template Examples**:
- "Communities missing demographic data"
- "Incomplete workshop assessments"
- "Data quality score by region"

---

### 3.7 Audit & Admin Domains (30 templates) ⬜

**Audit Domain** (15 templates):
- [ ] Create `new_domains/audit/` directory
- [ ] `change_tracking_queries.py` (10 templates)
- [ ] `activity_log_queries.py` (5 templates)

**Admin Domain** (15 templates):
- [ ] Create `new_domains/admin/` directory
- [ ] `system_health_queries.py` (10 templates)
- [ ] `user_management_queries.py` (5 templates)

**Success Criteria**:
- [ ] All 30 templates registered
- [ ] 100% test coverage
- [ ] Documentation generated

---

### 3.8 Phase 3 Validation ⬜

**Tasks**:
- [ ] Run full test suite (all 575 templates)
- [ ] Verify cross-domain queries work correctly
- [ ] Check performance (still <10ms match time)
- [ ] Verify memory usage (<25MB)
- [ ] Test lazy loading for new domains
- [ ] Run integration tests

**Success Criteria**:
- [ ] ✅ All 575 templates registered (385 → 575)
- [ ] ✅ Cross-domain queries functional
- [ ] ✅ Performance <10ms maintained
- [ ] ✅ Memory usage <25MB
- [ ] ✅ Lazy loading works for new domains

**Phase 3 Complete**: ⬜ (Mark when all tasks done)

---

## Phase 4: Enhancement & Optimization (Weeks 7-8) | PRIORITY: MEDIUM

**Goal**: Enhance entity extraction, response formatting, and prepare for production.

### 4.1 Enhanced Entity Extraction ⬜

**Tasks**:
- [ ] Add 10 new entity extractors:
  - [ ] LivelihoodExtractor
  - [ ] OrganizationTypeExtractor
  - [ ] PartnershipStatusExtractor
  - [ ] WorkshopTypeExtractor
  - [ ] PolicyCategoryExtractor
  - [ ] BudgetRangeExtractor
  - [ ] PopulationRangeExtractor
  - [ ] PriorityLevelExtractor
  - [ ] CompletionStatusExtractor
  - [ ] ReportTypeExtractor
- [ ] Update EntityExtractor class with new types
- [ ] Write unit tests for each extractor (>90% accuracy)
- [ ] Benchmark extraction performance (<5ms per query)

**Success Criteria**:
- [ ] 15+ entity types supported (5 existing + 10 new)
- [ ] Extraction accuracy >90% per entity type
- [ ] Extraction time <5ms per query

---

### 4.2 Response Formatting ⬜

**Tasks**:
- [ ] Create `utilities/response_formatter.py`
- [ ] Implement formatters for all query types:
  - [ ] COUNT → Number with context
  - [ ] LIST → HTML table
  - [ ] GET → Detail card
  - [ ] FIND → Filtered list
  - [ ] COMPARE → Comparison table
  - [ ] TREND → Line chart data
  - [ ] AGGREGATE → Summary statistics
  - [ ] RANK → Ranked list
  - [ ] VALIDATE → Validation report
  - [ ] EXPORT → Download link
- [ ] Add chart configuration for visualizations
- [ ] Write unit tests

**Success Criteria**:
- [ ] All 10 query types have formatters
- [ ] HTML output properly formatted
- [ ] Chart configurations valid

---

### 4.3 Auto-Generated Documentation ⬜

**Tasks**:
- [ ] Create `utilities/template_generator.py`
- [ ] Implement `generate_template_docs()` function
- [ ] Create Django management command:
  - [ ] `python manage.py generate_template_docs --all`
  - [ ] `python manage.py generate_template_docs --category {category}`
- [ ] Generate documentation for all 15 categories
- [ ] Set up auto-generation in CI/CD

**Success Criteria**:
- [ ] Documentation auto-generated for all categories
- [ ] Markdown files created in `docs/ai/queries/categories/`
- [ ] CI/CD integration complete

---

### 4.4 Deprecation Workflow ⬜

**Tasks**:
- [ ] Add deprecation fields to QueryTemplate:
  - [ ] `deprecated: bool`
  - [ ] `superseded_by: Optional[str]`
  - [ ] `version: str`
- [ ] Implement deprecation warning logging
- [ ] Create Django management command:
  - [ ] `python manage.py check_deprecated_templates --warn-if-old`
- [ ] Document deprecation process

**Success Criteria**:
- [ ] Deprecation fields added
- [ ] Warning system functional
- [ ] Management command works
- [ ] Process documented

---

### 4.5 Django Management Commands ⬜

**Tasks**:
- [ ] Create `common/management/commands/generate_template_docs.py`
- [ ] Create `common/management/commands/validate_templates.py`
- [ ] Create `common/management/commands/check_deprecated_templates.py`
- [ ] Create `common/management/commands/list_templates.py`
- [ ] Create `common/management/commands/template_stats.py`
- [ ] Create `common/management/commands/benchmark_templates.py`
- [ ] Write help text and documentation for each command

**Success Criteria**:
- [ ] All commands functional
- [ ] Help text clear and comprehensive
- [ ] Commands documented in README.md

---

### 4.6 Production Deployment ⬜

**Tasks**:
- [ ] Update production settings (if needed)
- [ ] Configure Redis cache for L2 caching
- [ ] Set up monitoring for template performance
- [ ] Deploy to staging environment
- [ ] Run smoke tests in staging
- [ ] Deploy to production
- [ ] Monitor first 24 hours
- [ ] Collect usage analytics

**Success Criteria**:
- [ ] Staging deployment successful
- [ ] Production deployment successful
- [ ] No performance regressions
- [ ] Monitoring active
- [ ] Usage analytics collecting

---

### 4.7 Phase 4 Validation ⬜

**Tasks**:
- [ ] Verify all 575 templates work in production
- [ ] Verify enhanced entity extraction (>90% accuracy)
- [ ] Verify response formatting for all query types
- [ ] Verify documentation auto-generation
- [ ] Verify deprecation workflow
- [ ] Performance check (still <10ms match time)
- [ ] Memory check (still <25MB)

**Success Criteria**:
- [ ] ✅ All enhancements deployed
- [ ] ✅ Entity extraction >90% accurate
- [ ] ✅ Response formatting works
- [ ] ✅ Documentation auto-generated
- [ ] ✅ Production-ready

**Phase 4 Complete**: ⬜ (Mark when all tasks done)

---

## Final Validation Checklist

### Performance Metrics ⬜

- [ ] Template match time: <10ms (99th percentile)
- [ ] Registry lookup time: <2ms
- [ ] Lazy load time: <20ms per category
- [ ] Cache hit rate: >75%
- [ ] Memory usage: <25MB
- [ ] Startup time: <100ms (cold), <20ms (warm)

### Quality Metrics ⬜

- [ ] Pattern match accuracy: >95%
- [ ] Query generation correctness: 100% (all tests pass)
- [ ] Entity extraction accuracy: >90%
- [ ] Test coverage: 100%

### Completeness ⬜

- [ ] 575 templates registered
- [ ] 15 categories created
- [ ] 10 query types supported
- [ ] 15+ entity types supported
- [ ] Documentation auto-generated for all categories

### Production Readiness ⬜

- [ ] All tests pass (100% pass rate)
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] Monitoring active
- [ ] No breaking changes

---

## Project Complete ⬜

**Final Stats**:
- Templates: 151 → 575 (281% increase)
- Categories: 7 → 15 (114% increase)
- Query Types: 5 → 10 (100% increase)
- Entity Types: 5 → 15 (200% increase)

**Performance Maintained**:
- Match time: <10ms ✅
- Memory: <25MB ✅
- Cache hit rate: >75% ✅

**Project Success**: ⬜ (Mark when all phases complete)

---

**Last Updated**: October 6, 2025
**Next Review**: After Phase 1 completion
