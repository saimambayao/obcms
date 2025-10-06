"""
Prompt Templates - Reusable prompt templates for AI operations.

This module provides:
- Bangsamoro cultural context templates
- Needs classification prompts
- Policy analysis templates
- Document generation templates
"""

from datetime import datetime
from typing import Dict, List, Optional


class PromptTemplates:
    """Collection of reusable prompt templates for AI operations."""

    # Cultural Context Template
    BANGSAMORO_CULTURAL_CONTEXT = """
You are assisting the Office for Other Bangsamoro Communities (OOBC).

CONTEXT:
- Serving Bangsamoro communities outside BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)
- Primary regions: IX (Zamboanga Peninsula), X (Northern Mindanao), XI (Davao), XII (SOCCSKSARGEN)
- Cultural sensitivity is CRITICAL
- Islamic values and traditions must be respected
- Traditional governance structures (Datu, Sultan) are important

CORE PRINCIPLES:
1. MARATABAT (Honor & Dignity) - Central to Bangsamoro identity
2. Islamic Compatibility - All solutions must respect Shariah principles
3. Community Consultation (Shura) - Decisions involve proper consultation
4. Extended Family Systems - Consider clan and kinship networks
5. Traditional Authority - Respect Datu, Sultan, and customary law (Adat)

ETHNOLINGUISTIC GROUPS:
- Maranao, Maguindanao, Tausug, Sama-Bajau, Yakan, Iranun, Kalagan, and others

ECONOMIC PATTERNS:
- Agriculture (rice, corn, coconut)
- Fishing and aquaculture
- Traditional crafts and weaving
- Halal industry development
"""

    # Needs Classification Template
    NEEDS_CLASSIFICATION_PROMPT = """
{cultural_context}

TASK: Analyze community data and classify primary needs.

NEED CATEGORIES:
1. HEALTH - Medical services, facilities, health education
2. EDUCATION - Schools, Madaris integration, teacher training
3. INFRASTRUCTURE - Roads, water, electricity, facilities
4. LIVELIHOOD - Economic opportunities, skills training
5. GOVERNANCE - Local governance, peace and order, legal services

COMMUNITY DATA:
{community_data}

INSTRUCTIONS:
1. Identify top 3 need categories based on data
2. Provide specific evidence from the data
3. Suggest culturally appropriate interventions
4. Consider Islamic values and traditional governance
5. Include implementation considerations

OUTPUT FORMAT:
## Primary Needs Classification

### 1. [Need Category]
- **Evidence**: [specific data points]
- **Priority Level**: High/Medium/Low
- **Cultural Considerations**: [relevant cultural factors]
- **Suggested Interventions**: [3-5 specific actions]

### 2. [Need Category]
...

### 3. [Need Category]
...

## Implementation Notes
- Cultural considerations
- Stakeholder engagement strategy
- Potential challenges
"""

    # Policy Analysis Template
    POLICY_ANALYSIS_PROMPT = """
{cultural_context}

TASK: Analyze policy recommendation and provide comprehensive insights.

POLICY DETAILS:
- Title: {policy_title}
- Category: {policy_category}
- Status: {policy_status}
- Description: {policy_description}

ANALYSIS FRAMEWORK:
1. SITUATION ANALYSIS - Current state and challenges
2. STAKEHOLDER MAPPING - Key actors and their interests
3. CULTURAL IMPACT ASSESSMENT - Effects on Bangsamoro communities
4. IMPLEMENTATION FEASIBILITY - Resources, timeline, barriers
5. RISK ASSESSMENT - Potential challenges and mitigation
6. SUCCESS METRICS - How to measure effectiveness

CULTURAL CONSIDERATIONS:
- Maratabat (honor/dignity) implications
- Islamic/Shariah compatibility
- Traditional governance integration
- Community consultation requirements
- Extended family/clan impacts

OUTPUT FORMAT:
## Policy Analysis: {policy_title}

### 1. Situation Analysis
[Current state, problems, context]

### 2. Stakeholder Mapping
| Stakeholder Group | Interest Level | Influence | Engagement Strategy |
|------------------|----------------|-----------|---------------------|
| Traditional Leaders | ... | ... | ... |
| Religious Leaders | ... | ... | ... |
| Community Members | ... | ... | ... |

### 3. Cultural Impact Assessment
- **Maratabat Considerations**: [analysis]
- **Islamic Compatibility**: [analysis]
- **Traditional Governance**: [analysis]
- **Community Acceptance**: [likelihood and factors]

### 4. Implementation Feasibility
- **Resources Required**: [budget, human resources, equipment]
- **Timeline**: [phases and milestones]
- **Barriers**: [potential obstacles]
- **Dependencies**: [prerequisites]

### 5. Risk Assessment
| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| [risk 1] | High/Med/Low | High/Med/Low | [strategy] |

### 6. Success Metrics
- **Quantitative**: [measurable indicators]
- **Qualitative**: [community perception, cultural acceptance]
- **Timeline**: [when to measure]

## Recommendations
1. [Key recommendation 1]
2. [Key recommendation 2]
...
"""

    # Document Generation Template
    POLICY_BRIEF_TEMPLATE = """
{cultural_context}

TASK: Generate a professional policy brief.

POLICY DATA:
- Title: {policy_title}
- Category: {policy_category}
- Problem Statement: {problem_statement}
- Proposed Solution: {proposed_solution}
- Expected Outcomes: {expected_outcomes}

DOCUMENT STRUCTURE:
1. Executive Summary (1 page)
2. Problem Analysis
3. Policy Recommendation
4. Implementation Strategy
5. Expected Impact
6. Cultural Considerations for Bangsamoro Communities
7. Resource Requirements
8. Risk Assessment
9. Monitoring and Evaluation
10. Conclusion and Next Steps

WRITING GUIDELINES:
- Professional government document tone
- Evidence-based analysis
- Culturally sensitive language
- Clear, actionable recommendations
- Proper citations and references
- Include Islamic terminology where appropriate

OUTPUT FORMAT:
# POLICY BRIEF

**Policy Title**: {policy_title}
**Category**: {policy_category}
**Date**: {current_date}
**Prepared by**: Office for Other Bangsamoro Communities (OOBC)

---

## EXECUTIVE SUMMARY
[Concise 1-page summary of problem, solution, and expected outcomes]

## 1. PROBLEM ANALYSIS
### 1.1 Current Situation
[Analysis of current state]

### 1.2 Key Challenges
[Main problems and barriers]

### 1.3 Affected Communities
[Which Bangsamoro communities are affected]

## 2. POLICY RECOMMENDATION
### 2.1 Proposed Solution
[Detailed solution description]

### 2.2 Rationale
[Why this solution is appropriate]

### 2.3 Evidence Base
[Supporting data and research]

## 3. IMPLEMENTATION STRATEGY
### 3.1 Phases
[Implementation phases and timeline]

### 3.2 Key Activities
[Specific activities per phase]

### 3.3 Stakeholder Roles
[Who does what]

## 4. EXPECTED IMPACT
### 4.1 Direct Benefits
[Immediate positive outcomes]

### 4.2 Long-term Benefits
[Sustainable impacts]

### 4.3 Success Indicators
[How to measure success]

## 5. CULTURAL CONSIDERATIONS
### 5.1 Islamic Compatibility
[Shariah compliance analysis]

### 5.2 Traditional Governance Integration
[How to work with Datu, Sultan, Adat systems]

### 5.3 Community Consultation Process
[Shura and engagement strategy]

### 5.4 Gender and Age Considerations
[Culturally appropriate participation]

## 6. RESOURCE REQUIREMENTS
### 6.1 Budget
[Financial requirements]

### 6.2 Human Resources
[Personnel needed]

### 6.3 Infrastructure and Equipment
[Physical resources]

## 7. RISK ASSESSMENT
| Risk Category | Description | Mitigation Strategy |
|--------------|-------------|---------------------|
| Cultural | [risks] | [strategies] |
| Implementation | [risks] | [strategies] |
| Financial | [risks] | [strategies] |

## 8. MONITORING AND EVALUATION
### 8.1 Key Performance Indicators
[Specific, measurable KPIs]

### 8.2 Data Collection Methods
[How to gather data]

### 8.3 Reporting Schedule
[When and how to report progress]

## 9. CONCLUSION AND NEXT STEPS
### 9.1 Summary
[Brief recap of key points]

### 9.2 Immediate Next Steps
1. [Action item 1]
2. [Action item 2]
...

### 9.3 Timeline
[When to start implementation]

---

**Office for Other Bangsamoro Communities (OOBC)**
*Serving Bangsamoro communities outside BARMM*
"""

    # Evidence Review Template
    EVIDENCE_REVIEW_PROMPT = """
{cultural_context}

TASK: Review and analyze evidence supporting policy recommendation.

EVIDENCE DATA:
{evidence_data}

EVALUATION CRITERIA:
1. **Relevance** - How well does evidence support the policy?
2. **Reliability** - Source credibility and methodology quality
3. **Validity** - Accuracy and representativeness of data
4. **Timeliness** - Recency and current applicability
5. **Cultural Appropriateness** - Relevance to Bangsamoro communities

ANALYSIS REQUIREMENTS:
- Apply rigorous evidence standards
- Consider cultural context in data interpretation
- Identify potential biases or limitations
- Suggest culturally appropriate data collection methods
- Recommend evidence-based improvements

OUTPUT FORMAT:
## Evidence Review

### Evidence Quality Assessment
| Evidence Source | Relevance | Reliability | Validity | Timeliness | Cultural Fit |
|----------------|-----------|-------------|----------|------------|--------------|
| [source 1] | Score/5 | Score/5 | Score/5 | Score/5 | Score/5 |

### Strengths
- [strength 1]
- [strength 2]
...

### Gaps and Limitations
- [gap 1]: [description and impact]
- [gap 2]: [description and impact]
...

### Cultural Context Issues
- [issue 1]: [how cultural factors affect data interpretation]
- [issue 2]: [how cultural factors affect data interpretation]
...

### Recommendations for Evidence Strengthening
1. [Recommendation 1]: [specific data collection method]
2. [Recommendation 2]: [additional evidence needed]
...

### Overall Assessment
- **Evidence Quality Score**: [X/10]
- **Recommendation**: [Sufficient/Insufficient/Needs Improvement]
- **Priority Gaps**: [top 3 evidence gaps to address]
"""

    @staticmethod
    def format_needs_classification(
        community_data: Dict,
        include_cultural_context: bool = True
    ) -> str:
        """Format needs classification prompt with community data."""
        cultural_context = (
            PromptTemplates.BANGSAMORO_CULTURAL_CONTEXT
            if include_cultural_context
            else ""
        )

        # Format community data as readable text
        data_text = "\n".join([
            f"- {key}: {value}"
            for key, value in community_data.items()
        ])

        return PromptTemplates.NEEDS_CLASSIFICATION_PROMPT.format(
            cultural_context=cultural_context,
            community_data=data_text
        )

    @staticmethod
    def format_policy_analysis(
        policy_title: str,
        policy_category: str,
        policy_status: str,
        policy_description: str,
        include_cultural_context: bool = True
    ) -> str:
        """Format policy analysis prompt."""
        cultural_context = (
            PromptTemplates.BANGSAMORO_CULTURAL_CONTEXT
            if include_cultural_context
            else ""
        )

        return PromptTemplates.POLICY_ANALYSIS_PROMPT.format(
            cultural_context=cultural_context,
            policy_title=policy_title,
            policy_category=policy_category,
            policy_status=policy_status,
            policy_description=policy_description
        )

    @staticmethod
    def format_policy_brief(
        policy_title: str,
        policy_category: str,
        problem_statement: str,
        proposed_solution: str,
        expected_outcomes: str,
        include_cultural_context: bool = True
    ) -> str:
        """Format policy brief generation prompt."""
        cultural_context = (
            PromptTemplates.BANGSAMORO_CULTURAL_CONTEXT
            if include_cultural_context
            else ""
        )

        current_date = datetime.now().strftime("%B %d, %Y")

        return PromptTemplates.POLICY_BRIEF_TEMPLATE.format(
            cultural_context=cultural_context,
            policy_title=policy_title,
            policy_category=policy_category,
            problem_statement=problem_statement,
            proposed_solution=proposed_solution,
            expected_outcomes=expected_outcomes,
            current_date=current_date
        )

    @staticmethod
    def format_evidence_review(
        evidence_data: List[Dict],
        include_cultural_context: bool = True
    ) -> str:
        """Format evidence review prompt."""
        cultural_context = (
            PromptTemplates.BANGSAMORO_CULTURAL_CONTEXT
            if include_cultural_context
            else ""
        )

        # Format evidence data
        evidence_text = "\n\n".join([
            f"**Evidence {i+1}**: {item.get('source', 'Unknown')}\n"
            f"- Type: {item.get('type', 'N/A')}\n"
            f"- Summary: {item.get('summary', 'N/A')}\n"
            f"- Date: {item.get('date', 'N/A')}"
            for i, item in enumerate(evidence_data)
        ])

        return PromptTemplates.EVIDENCE_REVIEW_PROMPT.format(
            cultural_context=cultural_context,
            evidence_data=evidence_text
        )
