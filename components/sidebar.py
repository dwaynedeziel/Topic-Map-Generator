from dataclasses import dataclass
from typing import List, Optional

import streamlit as st

from config.settings import SCOPE_COMPREHENSIVE, SCOPE_FOCUSED


@dataclass
class UserInputs:
    topic: str
    scope: str
    industry: Optional[str]
    audience: Optional[str]
    geo_focus: Optional[str]
    competitors: Optional[List[str]]
    existing_content: Optional[str]
    gdrive_enabled: bool
    gdrive_folder: Optional[str]


def render_sidebar(gdrive_available: bool = False) -> UserInputs:
    """Render the sidebar inputs and return collected user inputs."""
    with st.sidebar:
        st.header("Topic Map Configuration")

        topic = st.text_input(
            "Topic *",
            placeholder="e.g., Content Marketing, Personal Injury Law",
            help="The main subject to build the topical map around",
        )

        scope = st.radio(
            "Scope",
            options=[SCOPE_FOCUSED, SCOPE_COMPREHENSIVE],
            index=0,
            help="Focused: 15-25 topics. Comprehensive: 40-75 topics.",
        )

        st.divider()
        st.subheader("Optional Settings")

        industry = st.text_input(
            "Industry / Niche",
            placeholder="e.g., B2B SaaS, Home Services",
            help="Helps tailor the topic map to your specific industry",
        )

        audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Small business owners",
            help="Who the content is primarily targeting",
        )

        geo_focus = st.text_input(
            "Geographic Focus",
            placeholder="e.g., San Diego, CA or United States",
            help="Adds geographic relevance to topics",
        )

        competitors_raw = st.text_area(
            "Competitors to Analyze",
            placeholder="Comma-separated URLs or brand names",
            help="We'll analyze their content for topic ideas",
        )

        existing_content = st.text_area(
            "Existing Content to Exclude",
            placeholder="Topics or URLs you've already published",
            help="These topics will be excluded from the map",
        )

        # Google Drive integration
        gdrive_enabled = False
        gdrive_folder = None
        if gdrive_available:
            st.divider()
            st.subheader("Google Drive")
            gdrive_enabled = st.toggle("Enable Google Drive Upload", value=False)
            if gdrive_enabled:
                gdrive_folder = st.text_input(
                    "Drive Folder Name",
                    value="Topic Maps",
                    help="Folder in Google Drive to upload to (created if it doesn't exist)",
                )

        # Parse competitors
        competitors = None
        if competitors_raw:
            competitors = [
                c.strip() for c in competitors_raw.split(",") if c.strip()
            ]

        return UserInputs(
            topic=topic.strip() if topic else "",
            scope=scope,
            industry=industry.strip() if industry else None,
            audience=audience.strip() if audience else None,
            geo_focus=geo_focus.strip() if geo_focus else None,
            competitors=competitors,
            existing_content=existing_content.strip() if existing_content else None,
            gdrive_enabled=gdrive_enabled,
            gdrive_folder=gdrive_folder,
        )
