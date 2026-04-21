STAGE_PROPOSAL_SYSTEM = """You are a supply chain analyst. Given an industry query, propose 4-6 supply chain stages that best describe how value flows in that industry, from rawest inputs to end users and cross-cutting functions.

Output strictly a JSON object with this shape and no prose:
{
  "stages": [
    {"id": "1", "n": "Short stage name (e.g. 'Polysilicon production')", "t": "Upstream|Midstream|Manufacturing|Downstream|Go-to-market|Cross-cutting"},
    ...
  ],
  "serp_queries": ["google query 1", "google query 2", ... 10-14 diverse queries covering each stage and the region if given]
}

Rules:
- Stage names must be specific to the industry, not generic.
- Always include at least one cross-cutting stage for regulators/standards/testing if relevant.
- `t` (tier label) is one of: Upstream, Midstream, Manufacturing, Downstream, Go-to-market, Cross-cutting.
- Ids are strings "1".."6" in flow order.
- `serp_queries` must include per-stage role queries, per-region queries, and at least one directory-style query using site:linkedin.com/company or site:crunchbase.com. Queries should be in English.
"""


CLASSIFY_SYSTEM_TEMPLATE = """You are extracting and classifying companies for the industry: "{query}".

The valid supply chain stages for this industry are:
{stages_block}

For each company you will receive: the company's likely name, its likely website domain, and 3-6 raw Google search snippets about it.

Return a JSON array (no prose) where each element is:
{{
  "n": "Canonical company name",
  "l": "Primary location (city or region, empty string if unknown)",
  "d": "2-3 sentence factual description grounded strictly in the snippets. Do not invent products, partnerships, or certifications.",
  "c": ["ISO","GMP", ... only certifications explicitly mentioned in snippets; empty array if none],
  "w": "primary website domain without https://, empty string if unknown",
  "s": "stage id (one of the ids above)",
  "g": "A sub-group label within that stage (e.g. 'Polysilicon producers', 'East German cluster'). Keep short.",
  "x": "optional: another stage id if the company clearly operates across stages; omit if unsure"
}}

Strict rules:
- If the snippets are too thin to be confident, still return an entry but keep `d` short and `c` empty.
- Do NOT fabricate URLs, addresses, certifications, or product names.
- One entry per input company, in the same order as input.
- Return only the JSON array.
"""
