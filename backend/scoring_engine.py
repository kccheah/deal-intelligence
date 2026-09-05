"""
Claude AI-Powered Scoring Engine
Analyzes deals and properties to generate investment scores
"""

import json
import os
from anthropic import Anthropic
from typing import Dict, Any, Tuple

client = Anthropic()

# ============================================================================
# DEAL SCORING ENGINE
# ============================================================================

def score_deal(deal_data: Dict[str, Any]) -> Tuple[int, Dict[str, int], str]:
    """
    Score a deal using Claude AI

    Args:
        deal_data: Dictionary containing deal information

    Returns:
        Tuple of (score, score_breakdown, reasoning)
    """

    prompt = f"""
Analyze the following deal and provide an investment score (1-100) with breakdown.

DEAL DATA:
Company: {deal_data.get('company_name')}
Deal Type: {deal_data.get('deal_type')}
Deal Value: ${deal_data.get('deal_value_usd', 'Unknown'):,}
Industry: {deal_data.get('industry')}
Target Geography: {deal_data.get('target_geography')}
Acquiring Company: {deal_data.get('acquiring_company')}
Description: {deal_data.get('deal_description')}
Announced Date: {deal_data.get('announced_date')}

Please provide:
1. A breakdown score (1-100) for each factor:
   - Sector Attractiveness (1-100): How attractive is this industry?
   - Geography Score (1-100): How attractive is the target market?
   - Deal Size Score (1-100): Is the deal size reasonable and attractive?
   - Strategic Alignment (1-100): Does this signal a promising market trend?

2. A final weighted score (1-100) calculated as:
   (Sector * 0.25) + (Geography * 0.3) + (Size * 0.2) + (Strategic * 0.25)

3. A 2-3 sentence summary of key investment insights

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "sector_score": <number>,
    "geography_score": <number>,
    "size_score": <number>,
    "strategic_score": <number>,
    "final_score": <number>,
    "reasoning": "<2-3 sentence explanation>"
}}

Only respond with valid JSON, no additional text.
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    try:
        result = json.loads(response_text)

        score_breakdown = {
            "sector": result.get("sector_score", 0),
            "geography": result.get("geography_score", 0),
            "size": result.get("size_score", 0),
            "strategic": result.get("strategic_score", 0)
        }

        final_score = result.get("final_score", 50)
        reasoning = result.get("reasoning", "No reasoning provided")

        return final_score, score_breakdown, reasoning

    except json.JSONDecodeError:
        # Fallback scoring if Claude response is malformed
        print(f"Failed to parse Claude response: {response_text}")
        return 50, {"sector": 50, "geography": 50, "size": 50, "strategic": 50}, "Scoring engine error - using default"


# ============================================================================
# DEAL ENRICHMENT
# ============================================================================

def enrich_deal(deal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich deal data with analysis from Claude

    Args:
        deal_data: Raw deal data

    Returns:
        Enriched deal data with additional insights
    """

    prompt = f"""
Analyze this M&A/PE/JV deal and provide strategic insights:

Company: {deal_data.get('company_name')}
Deal Type: {deal_data.get('deal_type')}
Industry: {deal_data.get('industry')}
Geography: {deal_data.get('target_geography')}
Deal Value: ${deal_data.get('deal_value_usd', 'Unknown'):,}
Acquirer: {deal_data.get('acquiring_company')}
Description: {deal_data.get('deal_description')}

Provide:
1. Key market signals (1-2 sentences)
2. Strategic implications (1-2 sentences)
3. Risk factors (1-2 sentences)

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "market_signals": "<insights>",
    "strategic_implications": "<implications>",
    "risk_factors": "<risks>"
}}

Only respond with valid JSON.
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    try:
        enrichment = json.loads(response_text)
        deal_data["enrichment"] = enrichment
        return deal_data
    except json.JSONDecodeError:
        deal_data["enrichment"] = {
            "market_signals": "Unable to analyze",
            "strategic_implications": "Unable to analyze",
            "risk_factors": "Unable to analyze"
        }
        return deal_data


# ============================================================================
# PROPERTY DD SCORING
# ============================================================================

def score_property_dd(property_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any], str]:
    """
    Score a property investment using Claude AI

    Args:
        property_data: Dictionary containing property information

    Returns:
        Tuple of (investment_score, dd_breakdown, risk_level)
    """

    prompt = f"""
Analyze this property investment opportunity and provide a score:

PROPERTY DATA:
Address: {property_data.get('address')}
City: {property_data.get('city')}
Country: {property_data.get('country_code')}
Type: {property_data.get('property_type')}
Price: ${property_data.get('price_usd', 'Unknown'):,}
Size: {property_data.get('size_sqm')} sqm
Year Built: {property_data.get('year_built')}
Ownership Status: {property_data.get('ownership_legal_status')}
Foreign Ownership Allowed: {property_data.get('foreign_ownership_allowed')}
Freehold Eligible: {property_data.get('freehold_eligible')}

Please evaluate:
1. Legal Viability Score (1-100): Can a foreigner acquire this?
2. Market Attractiveness (1-100): Is the location/type attractive?
3. Regulatory Risk (1-100): What regulatory risks exist? (100 = no risk)
4. Value Score (1-100): Is the price reasonable?

Final Investment Score = (Legal * 0.3) + (Market * 0.3) + (Regulatory * 0.25) + (Value * 0.15)

Determine Risk Level: "low" (75+), "medium" (50-74), "high" (<50)

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "legal_score": <number>,
    "market_score": <number>,
    "regulatory_score": <number>,
    "value_score": <number>,
    "investment_score": <number>,
    "risk_level": "<low|medium|high>",
    "key_findings": "<2-3 sentence summary>"
}}

Only respond with valid JSON.
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=400,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    try:
        result = json.loads(response_text)

        dd_breakdown = {
            "legal_score": result.get("legal_score", 50),
            "market_score": result.get("market_score", 50),
            "regulatory_score": result.get("regulatory_score", 50),
            "value_score": result.get("value_score", 50),
            "key_findings": result.get("key_findings", "")
        }

        investment_score = result.get("investment_score", 50)
        risk_level = result.get("risk_level", "medium")

        return investment_score, dd_breakdown, risk_level

    except json.JSONDecodeError:
        print(f"Failed to parse Claude response: {response_text}")
        return 50, {
            "legal_score": 50,
            "market_score": 50,
            "regulatory_score": 50,
            "value_score": 50,
            "key_findings": "Scoring error"
        }, "medium"


# ============================================================================
# PROPERTY DD ANALYSIS
# ============================================================================

def analyze_property_dd(property_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate detailed DD analysis for a property

    Args:
        property_data: Property information

    Returns:
        Detailed DD analysis
    """

    prompt = f"""
Generate a due diligence analysis for this property investment:

Address: {property_data.get('address')}
City: {property_data.get('city')}
Country: {property_data.get('country_code')}
Ownership Status: {property_data.get('ownership_legal_status')}

Provide analysis for these DD categories:

1. LEGAL REVIEW: Key legal considerations and restrictions
2. TAX IMPLICATIONS: Tax obligations and withholding rates
3. REGULATORY COMPLIANCE: Capital controls, FDI rules
4. TITLE & LIEN: Typical concerns in this jurisdiction
5. TIMELINE TO ACQUISITION: Estimated process duration

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "legal_review": {{"concerns": "<key concerns>", "recommendations": "<actions>"}},
    "tax_implications": {{"obligations": "<taxes>", "withholding_rate": "<rate>"}},
    "regulatory_compliance": {{"capital_controls": "<info>", "fdi_status": "<allowed|restricted>"}},
    "title_and_lien": {{"process": "<typical process>", "timeline_months": <number>}},
    "acquisition_timeline": {{"estimated_months": <number>, "key_steps": "<steps>"}}
}}

Only respond with valid JSON.
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=800,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    try:
        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError:
        print(f"Failed to parse DD analysis: {response_text}")
        return {
            "legal_review": {"concerns": "Unable to analyze", "recommendations": ""},
            "tax_implications": {"obligations": "Unable to analyze", "withholding_rate": ""},
            "regulatory_compliance": {"capital_controls": "Unable to analyze", "fdi_status": ""},
            "title_and_lien": {"process": "Unable to analyze", "timeline_months": 0},
            "acquisition_timeline": {"estimated_months": 0, "key_steps": ""}
        }


# ============================================================================
# ALERT MESSAGE GENERATION
# ============================================================================

def generate_alert_message(deal_or_property: Dict[str, Any], alert_type: str) -> str:
    """
    Generate personalized alert message

    Args:
        deal_or_property: Deal or property data
        alert_type: 'deal' or 'property'

    Returns:
        Alert message string
    """

    if alert_type == "deal":
        prompt = f"""
Generate a concise, compelling alert message for this deal match:

Company: {deal_or_property.get('company_name')}
Type: {deal_or_property.get('deal_type')}
Value: ${deal_or_property.get('deal_value_usd', 'Unknown'):,}
Geography: {deal_or_property.get('target_geography')}
Score: {deal_or_property.get('score', 'N/A')}/100

Create a 1-2 sentence alert that highlights why this is relevant.
Format: "🎯 [Category] Alert: [Key insight]"
"""
    else:
        prompt = f"""
Generate a concise, compelling alert message for this property match:

Address: {deal_or_property.get('address')}
Price: ${deal_or_property.get('price_usd', 'Unknown'):,}
Type: {deal_or_property.get('property_type')}
Score: {deal_or_property.get('investment_score', 'N/A')}/100

Create a 1-2 sentence alert that highlights investment appeal.
Format: "🏠 [Category] Alert: [Key insight]"
"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=150,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()


if __name__ == "__main__":
    # Test scoring
    test_deal = {
        "company_name": "TechVenture Asia",
        "deal_type": "pe",
        "industry": "SaaS",
        "deal_value_usd": 25000000,
        "target_geography": "SG",
        "acquiring_company": "Regional PE Fund",
        "deal_description": "Series B funding for a Southeast Asian SaaS platform"
    }

    score, breakdown, reasoning = score_deal(test_deal)
    print(f"Deal Score: {score}/100")
    print(f"Breakdown: {breakdown}")
    print(f"Reasoning: {reasoning}")
