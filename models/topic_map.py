from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TopicMapEntry:
    level: str  # "Pillar" | "Cluster" | "Spoke"
    content_title: str
    primary_keyword: str
    user_intent: str  # "Informational" | "Navigational" | "Commercial Investigation" | "Transactional"
    semantic_entities: List[str]  # 3-5 related entities
    content_type: str
    rag_directions: str
    paa_questions: List[str]
    citations: List[str]
    parent_topic: Optional[str]
    priority_score: int  # 1-5
    word_count_range: str
    internal_link_targets: List[str]


VALID_LEVELS = {"Pillar", "Cluster", "Spoke"}

VALID_INTENTS = {
    "Informational",
    "Navigational",
    "Commercial Investigation",
    "Transactional",
}

CONTENT_TYPES = {
    "Pillar Page": "3000-5000",
    "Ultimate Guide": "2500-4000",
    "How-To Guide": "1500-2500",
    "Explainer": "1000-2000",
    "Comparison": "1500-2500",
    "Listicle": "1500-3000",
    "FAQ Page": "1000-2000",
    "Case Study": "1000-2000",
    "Checklist": "800-1500",
    "Statistics/Data Page": "1000-2000",
    "Glossary": "1500-3000",
    "Service Page": "800-1500",
    "Resource Hub": "1000-2000",
    "Product Page": "800-1500",
}


def validate_entry(entry: dict) -> List[str]:
    """Validate a single topic map entry dict. Returns list of error messages."""
    errors = []

    required_fields = [
        "level",
        "content_title",
        "primary_keyword",
        "user_intent",
        "semantic_entities",
        "content_type",
        "rag_directions",
        "paa_questions",
        "citations",
        "parent_topic",
        "priority_score",
        "word_count_range",
        "internal_link_targets",
    ]

    for f in required_fields:
        if f not in entry:
            errors.append(f"Missing required field: {f}")

    if not errors:
        if entry["level"] not in VALID_LEVELS:
            errors.append(
                f"Invalid level '{entry['level']}'. Must be one of: {VALID_LEVELS}"
            )

        if entry["user_intent"] not in VALID_INTENTS:
            errors.append(
                f"Invalid user_intent '{entry['user_intent']}'. Must be one of: {VALID_INTENTS}"
            )

        score = entry.get("priority_score", 0)
        if not isinstance(score, int) or score < 1 or score > 5:
            errors.append(
                f"Invalid priority_score '{score}'. Must be integer 1-5"
            )

        entities = entry.get("semantic_entities", [])
        if not isinstance(entities, list) or len(entities) < 3 or len(entities) > 5:
            errors.append(
                f"semantic_entities must have 3-5 items, got {len(entities) if isinstance(entities, list) else 'non-list'}"
            )

        paa = entry.get("paa_questions", [])
        if not isinstance(paa, list) or len(paa) < 2:
            errors.append(
                f"paa_questions must have at least 2 items, got {len(paa) if isinstance(paa, list) else 'non-list'}"
            )

        citations = entry.get("citations", [])
        if not isinstance(citations, list) or len(citations) < 1:
            errors.append(
                f"citations must have at least 1 item, got {len(citations) if isinstance(citations, list) else 'non-list'}"
            )

    return errors


def validate_topic_map(entries: List[dict]) -> List[str]:
    """Validate the full topic map structure. Returns list of error messages."""
    errors = []

    # Validate each entry individually
    for i, entry in enumerate(entries):
        entry_errors = validate_entry(entry)
        for err in entry_errors:
            errors.append(f"Entry {i} ({entry.get('content_title', 'unknown')}): {err}")

    if errors:
        return errors

    # Structural validations
    pillars = [e for e in entries if e["level"] == "Pillar"]
    clusters = [e for e in entries if e["level"] == "Cluster"]
    spokes = [e for e in entries if e["level"] == "Spoke"]

    if len(pillars) != 1:
        errors.append(f"Expected exactly 1 Pillar, found {len(pillars)}")
        return errors

    pillar_title = pillars[0]["content_title"]

    cluster_titles = {c["content_title"] for c in clusters}

    for cluster in clusters:
        parent = cluster.get("parent_topic", "")
        if parent and parent != pillar_title:
            errors.append(
                f"Cluster '{cluster['content_title']}' parent_topic "
                f"'{parent}' does not match Pillar title '{pillar_title}'"
            )

    for spoke in spokes:
        parent = spoke.get("parent_topic", "")
        if parent and parent not in cluster_titles:
            errors.append(
                f"Spoke '{spoke['content_title']}' parent_topic "
                f"'{parent}' does not match any Cluster title"
            )

    return errors


def dict_to_entry(data: dict) -> TopicMapEntry:
    """Convert a dict to a TopicMapEntry dataclass instance."""
    return TopicMapEntry(
        level=data.get("level", ""),
        content_title=data.get("content_title", ""),
        primary_keyword=data.get("primary_keyword", ""),
        user_intent=data.get("user_intent", ""),
        semantic_entities=data.get("semantic_entities", []),
        content_type=data.get("content_type", ""),
        rag_directions=data.get("rag_directions", ""),
        paa_questions=data.get("paa_questions", []),
        citations=data.get("citations", []),
        parent_topic=data.get("parent_topic", ""),
        priority_score=data.get("priority_score", 3),
        word_count_range=data.get("word_count_range", ""),
        internal_link_targets=data.get("internal_link_targets", []),
    )
