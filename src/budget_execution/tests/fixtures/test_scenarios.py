"""
Test data scenarios for budget system testing

Provides predefined test scenarios with realistic budget structures.
"""

from decimal import Decimal

# Budget size scenarios
BUDGET_TEST_SCENARIOS = {
    'small_budget': {
        'name': 'Small MOA Budget',
        'total': Decimal('10000000.00'),  # 10M
        'programs': 2,
        'line_items_per_program': 3,
        'description': 'Small ministry with basic programs'
    },
    'medium_budget': {
        'name': 'Medium MOA Budget',
        'total': Decimal('100000000.00'),  # 100M
        'programs': 5,
        'line_items_per_program': 10,
        'description': 'Medium-sized ministry with multiple programs'
    },
    'large_budget': {
        'name': 'Large MOA Budget',
        'total': Decimal('500000000.00'),  # 500M
        'programs': 15,
        'line_items_per_program': 30,
        'description': 'Large ministry with comprehensive programs'
    },
    'oobc_realistic': {
        'name': 'OOBC FY 2025 Budget',
        'total': Decimal('250000000.00'),  # 250M
        'programs': 8,
        'line_items_per_program': 20,
        'description': 'Realistic OOBC budget structure'
    }
}

# Financial constraint test cases
CONSTRAINT_TEST_CASES = [
    {
        'name': 'exceed_allotment',
        'allotment': Decimal('100000000.00'),
        'obligations': [
            Decimal('60000000.00'),
            Decimal('50000000.00')  # Total: 110M > 100M
        ],
        'should_fail': True,
        'expected_error': 'obligation_total_constraint'
    },
    {
        'name': 'within_allotment',
        'allotment': Decimal('100000000.00'),
        'obligations': [
            Decimal('40000000.00'),
            Decimal('30000000.00'),
            Decimal('25000000.00')  # Total: 95M < 100M
        ],
        'should_fail': False
    },
    {
        'name': 'exact_allotment',
        'allotment': Decimal('100000000.00'),
        'obligations': [
            Decimal('50000000.00'),
            Decimal('50000000.00')  # Total: 100M = 100M
        ],
        'should_fail': False
    },
    {
        'name': 'exceed_obligation',
        'obligation': Decimal('50000000.00'),
        'disbursements': [
            Decimal('30000000.00'),
            Decimal('25000000.00')  # Total: 55M > 50M
        ],
        'should_fail': True,
        'expected_error': 'disbursement_total_constraint'
    },
    {
        'name': 'progressive_disbursement_30_30_40',
        'obligation': Decimal('10000000.00'),
        'disbursements': [
            Decimal('3000000.00'),   # 30%
            Decimal('3000000.00'),   # 30%
            Decimal('4000000.00')    # 40%
        ],
        'should_fail': False,
        'description': 'Standard progressive payment pattern'
    },
    {
        'name': 'progressive_disbursement_50_50',
        'obligation': Decimal('20000000.00'),
        'disbursements': [
            Decimal('10000000.00'),  # 50%
            Decimal('10000000.00')   # 50%
        ],
        'should_fail': False,
        'description': 'Two-payment milestone pattern'
    }
]

# Quarterly allotment patterns
QUARTERLY_PATTERNS = {
    'equal_distribution': {
        'total': Decimal('100000000.00'),
        'Q1': Decimal('25000000.00'),
        'Q2': Decimal('25000000.00'),
        'Q3': Decimal('25000000.00'),
        'Q4': Decimal('25000000.00'),
        'description': 'Equal quarterly distribution'
    },
    'frontloaded': {
        'total': Decimal('100000000.00'),
        'Q1': Decimal('40000000.00'),
        'Q2': Decimal('30000000.00'),
        'Q3': Decimal('20000000.00'),
        'Q4': Decimal('10000000.00'),
        'description': 'Front-loaded for early execution'
    },
    'backloaded': {
        'total': Decimal('100000000.00'),
        'Q1': Decimal('10000000.00'),
        'Q2': Decimal('20000000.00'),
        'Q3': Decimal('30000000.00'),
        'Q4': Decimal('40000000.00'),
        'description': 'Back-loaded for year-end execution'
    },
    'realistic_oobc': {
        'total': Decimal('250000000.00'),
        'Q1': Decimal('50000000.00'),   # 20%
        'Q2': Decimal('75000000.00'),   # 30%
        'Q3': Decimal('75000000.00'),   # 30%
        'Q4': Decimal('50000000.00'),   # 20%
        'description': 'Realistic OOBC pattern'
    }
}

# Budget category distributions
CATEGORY_DISTRIBUTIONS = {
    'personnel_heavy': {
        'personnel': Decimal('0.60'),   # 60%
        'operating': Decimal('0.30'),   # 30%
        'capital': Decimal('0.10'),     # 10%
        'description': 'Service-oriented program'
    },
    'capital_heavy': {
        'personnel': Decimal('0.20'),   # 20%
        'operating': Decimal('0.20'),   # 20%
        'capital': Decimal('0.60'),     # 60%
        'description': 'Infrastructure program'
    },
    'balanced': {
        'personnel': Decimal('0.40'),   # 40%
        'operating': Decimal('0.40'),   # 40%
        'capital': Decimal('0.20'),     # 20%
        'description': 'Balanced program'
    },
    'oobc_typical': {
        'personnel': Decimal('0.45'),   # 45%
        'operating': Decimal('0.35'),   # 35%
        'capital': Decimal('0.20'),     # 20%
        'description': 'Typical OOBC distribution'
    }
}

# Utilization rate scenarios
UTILIZATION_SCENARIOS = [
    {
        'name': 'excellent_utilization',
        'approved': Decimal('100000000.00'),
        'allotted': Decimal('95000000.00'),   # 95%
        'obligated': Decimal('90000000.00'),  # 90%
        'disbursed': Decimal('85000000.00'),  # 85%
        'target_rate': 85.0,
        'assessment': 'Excellent execution'
    },
    {
        'name': 'good_utilization',
        'approved': Decimal('100000000.00'),
        'allotted': Decimal('85000000.00'),   # 85%
        'obligated': Decimal('75000000.00'),  # 75%
        'disbursed': Decimal('65000000.00'),  # 65%
        'target_rate': 65.0,
        'assessment': 'Good execution'
    },
    {
        'name': 'poor_utilization',
        'approved': Decimal('100000000.00'),
        'allotted': Decimal('50000000.00'),   # 50%
        'obligated': Decimal('30000000.00'),  # 30%
        'disbursed': Decimal('15000000.00'),  # 15%
        'target_rate': 15.0,
        'assessment': 'Poor execution - needs improvement'
    },
    {
        'name': 'year_end_rush',
        'approved': Decimal('100000000.00'),
        'allotted': Decimal('95000000.00'),   # 95%
        'obligated': Decimal('90000000.00'),  # 90%
        'disbursed': Decimal('40000000.00'),  # 40%
        'target_rate': 40.0,
        'assessment': 'High obligation, low disbursement - year-end rush'
    }
]

# Performance test scenarios
PERFORMANCE_TEST_SCENARIOS = {
    'bulk_line_items': {
        'program_budgets': 1,
        'line_items_per_program': 100,
        'target_time_seconds': 2.0,
        'description': 'Bulk line item creation'
    },
    'complex_query': {
        'program_budgets': 50,
        'line_items_per_program': 20,
        'target_time_seconds': 1.0,
        'description': 'Dashboard query with 50 programs'
    },
    'financial_validation': {
        'allotments': 10,
        'obligations_per_allotment': 100,
        'target_time_seconds': 5.0,
        'description': 'Validate 1000 obligations'
    },
    'aggregation_heavy': {
        'proposals': 10,
        'programs_per_proposal': 20,
        'line_items_per_program': 50,
        'target_time_seconds': 3.0,
        'description': 'Multi-level aggregation across 10,000 line items'
    }
}

# Workflow test scenarios
WORKFLOW_SCENARIOS = {
    'standard_approval': {
        'steps': [
            {'action': 'create_draft', 'expected_status': 'draft'},
            {'action': 'submit', 'expected_status': 'submitted'},
            {'action': 'review', 'expected_status': 'under_review'},
            {'action': 'approve', 'expected_status': 'approved'}
        ],
        'description': 'Standard approval workflow'
    },
    'revision_required': {
        'steps': [
            {'action': 'create_draft', 'expected_status': 'draft'},
            {'action': 'submit', 'expected_status': 'submitted'},
            {'action': 'reject', 'expected_status': 'revision_required'},
            {'action': 'revise', 'expected_status': 'draft'},
            {'action': 'resubmit', 'expected_status': 'submitted'},
            {'action': 'approve', 'expected_status': 'approved'}
        ],
        'description': 'Workflow with revision cycle'
    }
}

# Export all scenarios
__all__ = [
    'BUDGET_TEST_SCENARIOS',
    'CONSTRAINT_TEST_CASES',
    'QUARTERLY_PATTERNS',
    'CATEGORY_DISTRIBUTIONS',
    'UTILIZATION_SCENARIOS',
    'PERFORMANCE_TEST_SCENARIOS',
    'WORKFLOW_SCENARIOS'
]
