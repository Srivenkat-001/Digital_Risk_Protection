import streamlit as st

from ui.components.charts import render_severity_donut, render_status_bar


def test_severity_chart_builds_and_renders(monkeypatch):
    figures = []
    monkeypatch.setattr(st, "plotly_chart", lambda figure, **kwargs: figures.append(figure))

    render_severity_donut({"High": 2, "Low": 1})

    assert len(figures) == 1
    assert list(figures[0].data[0].labels) == ["Critical", "High", "Medium", "Low"]


def test_status_chart_uses_supported_axis_tickfont(monkeypatch):
    figures = []
    monkeypatch.setattr(st, "plotly_chart", lambda figure, **kwargs: figures.append(figure))

    render_status_bar({"New": 2, "Investigating": 1})

    assert len(figures) == 1
    assert figures[0].layout.xaxis.tickfont.color == "#8b949e"
    assert figures[0].layout.yaxis.tickfont.color == "#f0f6fc"
