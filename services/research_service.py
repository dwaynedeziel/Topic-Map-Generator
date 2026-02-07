import time
from datetime import datetime
from typing import List, Optional

import streamlit as st
from tavily import TavilyClient

from config.settings import (
    TAVILY_API_KEY,
    TAVILY_MAX_RESULTS,
    TAVILY_RATE_LIMIT_DELAY,
    TAVILY_SEARCH_DEPTH,
)


def build_research_queries(
    topic: str,
    industry: Optional[str] = None,
    competitors: Optional[List[str]] = None,
) -> List[str]:
    """Build the list of research queries for the given topic."""
    current_year = datetime.now().year
    queries = [
        f"{topic}",
        f"{topic} guide",
        f"{topic} how to",
        f"what is {topic}",
        f"{topic} questions people ask",
        f"{topic} statistics {current_year}",
        f"{topic} vs",
        f"best {topic}",
        f"{topic} {industry}" if industry else f"{topic} trends",
        f"{topic} common mistakes",
    ]

    if competitors:
        for competitor in competitors[:3]:
            comp = competitor.strip()
            if comp:
                queries.append(f"site:{comp} {topic}")

    return queries


@st.cache_data(show_spinner=False)
def perform_research(
    topic: str,
    industry: Optional[str] = None,
    competitors: Optional[List[str]] = None,
) -> dict:
    """Execute all research queries via Tavily and compile results.

    Returns a dict with 'compiled_text' (str) and 'summary' (str).
    Results are cached by (topic, industry, competitors tuple).
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not configured.")

    client = TavilyClient(api_key=TAVILY_API_KEY)
    queries = build_research_queries(topic, industry, competitors)

    all_answers = []
    all_urls = []
    all_snippets = []
    all_questions = []
    all_stats = []
    content_types_seen = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, query in enumerate(queries):
        status_text.text(f"Researching: {query}")
        progress_bar.progress((i + 1) / len(queries))

        try:
            result = client.search(
                query=query,
                search_depth=TAVILY_SEARCH_DEPTH,
                max_results=TAVILY_MAX_RESULTS,
                include_answer=True,
                include_raw_content=False,
            )

            if result.get("answer"):
                all_answers.append(f"**Query: {query}**\n{result['answer']}")

            for r in result.get("results", []):
                url = r.get("url", "")
                title = r.get("title", "")
                snippet = r.get("content", "")

                if url and title:
                    all_urls.append(f"- [{title}]({url})")
                if snippet:
                    all_snippets.append(f"[{title}]: {snippet}")

                # Detect questions in titles/snippets
                for text in [title, snippet]:
                    if text and "?" in text:
                        sentences = text.split("?")
                        for s in sentences[:-1]:
                            q = s.strip().split(".")[-1].strip() + "?"
                            if len(q) > 15 and len(q) < 200:
                                all_questions.append(q)

                # Detect statistics
                if snippet:
                    for indicator in ["%", "percent", "billion", "million", "thousand", "$"]:
                        if indicator in snippet.lower():
                            all_stats.append(snippet[:300])
                            break

                # Detect content types
                title_lower = title.lower() if title else ""
                for ct in ["guide", "how to", "vs", "comparison", "review", "best", "checklist", "faq"]:
                    if ct in title_lower:
                        content_types_seen.append(ct)

        except Exception as e:
            # Skip failed queries, continue with others
            st.warning(f"Research query skipped: {query} ({e})")

        if i < len(queries) - 1:
            time.sleep(TAVILY_RATE_LIMIT_DELAY)

    progress_bar.empty()
    status_text.empty()

    # Compile into a structured research document
    sections = []

    if all_answers:
        sections.append("### AI-Generated Research Summaries\n")
        sections.append("\n\n".join(all_answers))

    if all_urls:
        sections.append("\n### Top-Ranking URLs and Titles\n")
        unique_urls = list(dict.fromkeys(all_urls))[:30]
        sections.append("\n".join(unique_urls))

    if all_snippets:
        sections.append("\n### Content Snippets from Search Results\n")
        unique_snippets = list(dict.fromkeys(all_snippets))[:25]
        sections.append("\n\n".join(unique_snippets))

    if all_stats:
        sections.append("\n### Statistics and Data Points Found\n")
        unique_stats = list(dict.fromkeys(all_stats))[:15]
        for stat in unique_stats:
            sections.append(f"- {stat}")

    if all_questions:
        sections.append("\n### Questions Identified in Results\n")
        unique_questions = list(dict.fromkeys(all_questions))[:20]
        for q in unique_questions:
            sections.append(f"- {q}")

    if content_types_seen:
        sections.append("\n### Content Types Observed Ranking\n")
        from collections import Counter
        ct_counts = Counter(content_types_seen)
        for ct, count in ct_counts.most_common():
            sections.append(f"- {ct}: {count} occurrences")

    compiled_text = "\n".join(sections)

    # Build a short summary
    summary_parts = [
        f"Executed {len(queries)} research queries for '{topic}'.",
        f"Found {len(all_urls)} unique URLs,",
        f"{len(all_snippets)} content snippets,",
        f"{len(all_stats)} data points,",
        f"and {len(all_questions)} questions.",
    ]
    summary = " ".join(summary_parts)

    return {
        "compiled_text": compiled_text,
        "summary": summary,
        "query_count": len(queries),
        "url_count": len(set(all_urls)),
        "snippet_count": len(all_snippets),
        "stats_count": len(all_stats),
        "questions_count": len(all_questions),
    }
