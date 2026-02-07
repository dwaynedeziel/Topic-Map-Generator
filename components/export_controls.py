from typing import List, Optional

import streamlit as st

from services.csv_service import (
    generate_csv_bytes,
    generate_filename,
    topic_map_to_dataframe,
)


def render_export_controls(
    entries: List[dict],
    topic: str,
    gdrive_enabled: bool = False,
    gdrive_folder: Optional[str] = None,
) -> None:
    """Render CSV download and optional Google Drive upload controls."""
    df = topic_map_to_dataframe(entries)
    csv_bytes = generate_csv_bytes(df)
    filename = generate_filename(topic)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        if gdrive_enabled:
            if st.button("Upload to Google Drive", use_container_width=True):
                try:
                    from services.gdrive_service import upload_to_drive

                    with st.spinner("Uploading to Google Drive..."):
                        link = upload_to_drive(
                            csv_bytes=csv_bytes,
                            filename=filename,
                            folder_name=gdrive_folder or "Topic Maps",
                        )
                    if link:
                        st.success(f"Uploaded! [Open in Google Drive]({link})")
                    else:
                        st.error("Upload completed but no link was returned.")
                except ImportError:
                    st.error("Google Drive dependencies are not installed.")
                except Exception as e:
                    st.error(f"Google Drive upload failed: {e}")
