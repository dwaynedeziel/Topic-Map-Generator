from typing import List

import pandas as pd
import streamlit as st

from services.csv_service import topic_map_to_dataframe


def render_statistics(entries: List[dict]) -> None:
    """Render topic map summary statistics."""
    total = len(entries)
    pillars = sum(1 for e in entries if e.get("level") == "Pillar")
    clusters = sum(1 for e in entries if e.get("level") == "Cluster")
    spokes = sum(1 for e in entries if e.get("level") == "Spoke")

    intent_counts = {}
    for e in entries:
        intent = e.get("user_intent", "Unknown")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Topics", total)
    col2.metric("Pillars", pillars)
    col3.metric("Clusters", clusters)
    col4.metric("Spokes", spokes)

    st.markdown("**Intent Distribution:**")
    intent_cols = st.columns(len(intent_counts))
    for i, (intent, count) in enumerate(sorted(intent_counts.items())):
        intent_cols[i].metric(intent, count)


def render_hierarchy(entries: List[dict]) -> None:
    """Render a tree view of the topic hierarchy."""
    pillar = next((e for e in entries if e.get("level") == "Pillar"), None)
    if not pillar:
        st.warning("No Pillar topic found in the map.")
        return

    clusters = [e for e in entries if e.get("level") == "Cluster"]
    spokes = [e for e in entries if e.get("level") == "Spoke"]

    # Build a lookup of cluster title -> spokes
    cluster_spokes = {}
    for spoke in spokes:
        parent = spoke.get("parent_topic", "")
        if parent not in cluster_spokes:
            cluster_spokes[parent] = []
        cluster_spokes[parent].append(spoke)

    tree_lines = []
    p_title = pillar.get("content_title", "Pillar")
    p_score = pillar.get("priority_score", "")
    tree_lines.append(f"**{p_title}** (Priority: {p_score})")

    for j, cluster in enumerate(clusters):
        c_title = cluster.get("content_title", "Cluster")
        c_score = cluster.get("priority_score", "")
        is_last_cluster = j == len(clusters) - 1
        prefix = "\u2514\u2500\u2500" if is_last_cluster else "\u251c\u2500\u2500"
        tree_lines.append(f"&nbsp;&nbsp;{prefix} **{c_title}** (Priority: {c_score})")

        child_spokes = cluster_spokes.get(c_title, [])
        for k, spoke in enumerate(child_spokes):
            s_title = spoke.get("content_title", "Spoke")
            s_score = spoke.get("priority_score", "")
            is_last_spoke = k == len(child_spokes) - 1
            indent = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" if is_last_cluster else "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            s_prefix = "\u2514\u2500\u2500" if is_last_spoke else "\u251c\u2500\u2500"
            tree_lines.append(
                f"{indent}{s_prefix} {s_title} (Priority: {s_score})"
            )

    st.markdown("\n\n".join(tree_lines), unsafe_allow_html=True)


def _color_level(row: pd.Series) -> list:
    """Return row background colors based on Level column."""
    level = row.get("Level", "")
    if level == "Pillar":
        return ["background-color: #dbeafe"] * len(row)
    elif level == "Cluster":
        return ["background-color: #dcfce7"] * len(row)
    return [""] * len(row)


def render_data_table(entries: List[dict]) -> None:
    """Render the interactive, filterable data table."""
    df = topic_map_to_dataframe(entries)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        level_filter = st.multiselect(
            "Filter by Level",
            options=["Pillar", "Cluster", "Spoke"],
            default=["Pillar", "Cluster", "Spoke"],
        )
    with col2:
        intent_options = df["User Intent"].unique().tolist()
        intent_filter = st.multiselect(
            "Filter by Intent",
            options=intent_options,
            default=intent_options,
        )
    with col3:
        type_options = df["Content Type"].unique().tolist()
        type_filter = st.multiselect(
            "Filter by Content Type",
            options=type_options,
            default=type_options,
        )
    with col4:
        priority_filter = st.slider(
            "Min Priority Score",
            min_value=1,
            max_value=5,
            value=1,
        )

    # Apply filters
    filtered = df[
        (df["Level"].isin(level_filter))
        & (df["User Intent"].isin(intent_filter))
        & (df["Content Type"].isin(type_filter))
        & (df["Priority Score"] >= priority_filter)
    ]

    st.write(f"Showing {len(filtered)} of {len(df)} topics")

    styled = filtered.style.apply(_color_level, axis=1)
    st.dataframe(
        styled,
        use_container_width=True,
        height=600,
    )
