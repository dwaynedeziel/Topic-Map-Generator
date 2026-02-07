import streamlit as st

from config.settings import (
    ANTHROPIC_API_KEY,
    APP_ICON,
    APP_LAYOUT,
    APP_TITLE,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    TAVILY_API_KEY,
)
from components.sidebar import render_sidebar
from components.results_table import (
    render_data_table,
    render_hierarchy,
    render_statistics,
)
from components.export_controls import render_export_controls

st.set_page_config(
    layout=APP_LAYOUT,
    page_title=APP_TITLE,
    page_icon=APP_ICON,
)

st.markdown(
    """
<style>
    .stApp { max-width: 1400px; margin: 0 auto; }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown(
    "Generate a comprehensive, RAG-optimized topical map for SEO and AEO content strategy."
)


def _check_api_keys() -> bool:
    """Check if required API keys are configured. Show messages if not."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")

    if missing:
        st.error(
            f"Missing required API keys: {', '.join(missing)}. "
            "Please set them in your `.env` file or Streamlit secrets."
        )
        st.info(
            "**Setup instructions:**\n\n"
            "1. Copy `.env.example` to `.env`\n"
            "2. Add your [Anthropic API key](https://console.anthropic.com/)\n"
            "3. Add your [Tavily API key](https://tavily.com/)\n"
            "4. Restart the app"
        )
        return False
    return True


def main() -> None:
    gdrive_available = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    inputs = render_sidebar(gdrive_available=gdrive_available)

    if not _check_api_keys():
        return

    # Generate button in the sidebar
    with st.sidebar:
        st.divider()
        generate_clicked = st.button(
            "Generate Topic Map",
            type="primary",
            use_container_width=True,
            disabled=not inputs.topic,
        )
        if not inputs.topic:
            st.caption("Enter a topic above to get started.")

    # Handle generation
    if generate_clicked and inputs.topic:
        _run_generation(inputs)

    # Display stored results
    if "topic_map_entries" in st.session_state and st.session_state.topic_map_entries:
        _display_results(inputs)


def _run_generation(inputs) -> None:
    """Execute the research and AI generation pipeline."""
    from services.research_service import perform_research
    from services.ai_service import generate_topic_map

    # Phase 2: Research
    with st.status("Researching topic...", expanded=True) as status:
        st.write("Querying Tavily for research data...")
        try:
            research = perform_research(
                topic=inputs.topic,
                industry=inputs.industry,
                competitors=inputs.competitors,
            )
            st.session_state.research_data = research
            status.update(label="Research complete!", state="complete")
        except Exception as e:
            status.update(label="Research failed", state="error")
            st.error(f"Research failed: {e}")
            return

    # Phase 3: AI Processing
    with st.status("Building topic map with AI...", expanded=True) as status:
        st.write("Analyzing research and generating topic map...")
        try:
            entries = generate_topic_map(
                topic=inputs.topic,
                scope=inputs.scope,
                industry=inputs.industry or "",
                audience=inputs.audience or "",
                geo_focus=inputs.geo_focus or "",
                competitors=", ".join(inputs.competitors) if inputs.competitors else "",
                existing_content=inputs.existing_content or "",
                compiled_research=research["compiled_text"],
            )
            st.session_state.topic_map_entries = entries
            st.session_state.topic_map_topic = inputs.topic
            status.update(label="Topic map generated!", state="complete")
        except Exception as e:
            status.update(label="Generation failed", state="error")
            st.error(f"Topic map generation failed: {e}")
            return

    st.success(
        f"Topic map generated with {len(entries)} topics! "
        "Scroll down to explore the results."
    )


def _display_results(inputs) -> None:
    """Display the stored topic map results."""
    entries = st.session_state.topic_map_entries
    topic = st.session_state.get("topic_map_topic", inputs.topic)

    # Research summary
    if "research_data" in st.session_state:
        with st.expander("Research Summary", expanded=False):
            research = st.session_state.research_data
            st.write(research.get("summary", ""))
            st.markdown(f"- **Queries executed:** {research.get('query_count', 0)}")
            st.markdown(f"- **URLs found:** {research.get('url_count', 0)}")
            st.markdown(f"- **Content snippets:** {research.get('snippet_count', 0)}")
            st.markdown(f"- **Data points:** {research.get('stats_count', 0)}")
            st.markdown(f"- **Questions found:** {research.get('questions_count', 0)}")

    # Tabs for different views
    tab_stats, tab_table, tab_tree, tab_export = st.tabs(
        ["Statistics", "Data Table", "Topic Hierarchy", "Export"]
    )

    with tab_stats:
        render_statistics(entries)

    with tab_table:
        render_data_table(entries)

    with tab_tree:
        render_hierarchy(entries)

    with tab_export:
        render_export_controls(
            entries=entries,
            topic=topic,
            gdrive_enabled=inputs.gdrive_enabled,
            gdrive_folder=inputs.gdrive_folder,
        )


if __name__ == "__main__":
    main()
