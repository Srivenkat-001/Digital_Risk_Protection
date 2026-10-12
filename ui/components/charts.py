"""
Plotly visualization charts for cybersecurity metrics and distributions.
"""


import plotly.graph_objects as go
import streamlit as st

# Color palette mapped to BrandPhantom severity
SEVERITY_COLORS = {
    "Critical": "#f85149",
    "High": "#d29922",
    "Medium": "#e3b341",
    "Low": "#3fb950",
}

STATUS_COLORS = {
    "New": "#58a6ff",
    "Needs Review": "#e3b341",
    "Investigating": "#d29922",
    "Confirmed Threat": "#f85149",
    "False Positive": "#8b949e",
    "Resolved": "#3fb950",
    "Dismissed": "#6e7681",
}

def render_severity_donut(severity_counts: dict[str, int]):
    """Renders a Plotly donut chart of finding severity distribution."""
    labels = ["Critical", "High", "Medium", "Low"]
    values = [severity_counts.get(sev, 0) for sev in labels]
    colors = [SEVERITY_COLORS[sev] for sev in labels]

    if sum(values) == 0:
        st.info("No findings available to display severity distribution.")
        return

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.65,
                marker=dict(colors=colors),
                textinfo="label+value",
                hoverinfo="label+value+percent",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Findings by Severity", font=dict(color="#f0f6fc", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(font=dict(color="#8b949e"), orientation="h", yanchor="bottom", y=-0.2),
        height=260,
    )

    st.plotly_chart(fig, use_container_width=True)

def render_status_bar(status_counts: dict[str, int]):
    """Renders a horizontal bar chart of triage statuses."""
    statuses = list(STATUS_COLORS.keys())
    values = [status_counts.get(s, 0) for s in statuses]
    colors = [STATUS_COLORS[s] for s in statuses]

    if sum(values) == 0:
        st.info("No findings available to display status breakdown.")
        return

    fig = go.Figure(
        data=[
            go.Bar(
                x=values,
                y=statuses,
                orientation="h",
                marker=dict(color=colors),
                text=values,
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Triage Review Status", font=dict(color="#f0f6fc", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#30363d", tickfont=dict(color="#8b949e")),
        yaxis=dict(autorange="reversed", tickfont=dict(color="#f0f6fc")),
        margin=dict(t=30, b=10, l=10, r=10),
        height=260,
    )

    st.plotly_chart(fig, use_container_width=True)
