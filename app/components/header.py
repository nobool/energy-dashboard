import streamlit as st
from components.metrics import load_data
import pandas as pd

def render_header(title):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(title)
    with col2:
        try:
            smp, _, _ = load_data()
            if not smp.empty and 'Datetime' in smp.columns:
                min_date = (smp['Datetime'].min() + pd.Timedelta(days=1)).strftime('%d %b')
                max_date = smp['Datetime'].max().strftime('%d %b %Y')
                date_str = min_date if min_date == max_date else f"{min_date} – {max_date}"
                
                badge_html = f"""
                <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; padding-top: 2rem;">
                    <div style="background-color: rgba(128, 128, 128, 0.1); border: 1px solid rgba(128, 128, 128, 0.2); 
                                color: inherit; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 500;">
                        📅 {date_str}
                    </div>
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)
        except Exception:
            pass
