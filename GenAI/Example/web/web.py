import streamlit as st

analyze_log = st.Page("analyze_logs.py", title="Analyze Logs", icon="🌀")
triage_case_page = st.Page("triage_case.py", title="Triage Automation Case", icon="📊")
triage_bug_page = st.Page("triage_bug.py", title="Triage Bug", icon="🐞")
pg = st.navigation([analyze_log, triage_case_page, triage_bug_page])

pg.run()      