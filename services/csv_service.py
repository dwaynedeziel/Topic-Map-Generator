import re
from datetime import datetime
from typing import List

import pandas as pd


def _join_list(items) -> str:
    """Join a list with pipe separator for CSV export."""
    if isinstance(items, list):
        return "|".join(str(item) for item in items)
    return str(items)


def topic_map_to_dataframe(entries: List[dict]) -> pd.DataFrame:
    """Convert a list of topic map entry dicts to a pandas DataFrame."""
    rows = []
    for entry in entries:
        rows.append(
            {
                "Level": entry.get("level", ""),
                "Content Title": entry.get("content_title", ""),
                "Primary Keyword": entry.get("primary_keyword", ""),
                "User Intent": entry.get("user_intent", ""),
                "Semantic Entities": _join_list(entry.get("semantic_entities", [])),
                "Content Type": entry.get("content_type", ""),
                "RAG Directions": entry.get("rag_directions", ""),
                "PAA Questions": _join_list(entry.get("paa_questions", [])),
                "Citations": _join_list(entry.get("citations", [])),
                "Parent Topic": entry.get("parent_topic", ""),
                "Priority Score": entry.get("priority_score", 0),
                "Word Count Range": entry.get("word_count_range", ""),
                "Internal Link Targets": _join_list(
                    entry.get("internal_link_targets", [])
                ),
            }
        )
    return pd.DataFrame(rows)


def generate_csv_bytes(df: pd.DataFrame) -> bytes:
    """Generate CSV content as bytes from a DataFrame."""
    return df.to_csv(index=False).encode("utf-8")


def generate_filename(topic: str) -> str:
    """Generate a filename for the CSV export."""
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
    date_str = datetime.now().strftime("%Y%m%d")
    return f"topical_map_{slug}_{date_str}.csv"
