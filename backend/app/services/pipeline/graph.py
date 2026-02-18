"""
AdGen Pipeline Graph
LangGraph StateGraph 정의
"""
from typing import Literal
from langgraph.graph import StateGraph, END

from app.services.pipeline.state import PipelineState
from app.services.pipeline.nodes import (
    node_select_image,
    node_remove_background,
    node_virtual_fitting,
    node_generate_background,
    node_generate_caption,
    node_generate_html,
    node_save_image,
)


def should_continue(state: PipelineState) -> Literal["continue", "stop"]:
    """
    각 노드 완료 후 다음 단계로 진행할지 결정
    실패 시 파이프라인 중단
    """
    if state["status"] == "failed":
        return "stop"
    return "continue"


def build_pipeline_graph() -> StateGraph:
    """
    AdGen 파이프라인 그래프 생성

    흐름:
    select_image → remove_background → virtual_fitting
    → generate_background → generate_caption
    → generate_html → save_image → END

    각 노드 사이: 실패 감지 조건부 엣지
    """
    graph = StateGraph(PipelineState)

    # ===== 노드 등록 =====
    graph.add_node("select_image", node_select_image)
    graph.add_node("remove_background", node_remove_background)
    graph.add_node("virtual_fitting", node_virtual_fitting)
    graph.add_node("generate_background", node_generate_background)
    graph.add_node("generate_caption", node_generate_caption)
    graph.add_node("generate_html", node_generate_html)
    graph.add_node("save_image", node_save_image)

    # ===== 진입점 =====
    graph.set_entry_point("select_image")

    # ===== 조건부 엣지 (실패 시 END) =====
    graph.add_conditional_edges(
        "select_image",
        should_continue,
        {"continue": "remove_background", "stop": END},
    )
    graph.add_conditional_edges(
        "remove_background",
        should_continue,
        {"continue": "virtual_fitting", "stop": END},
    )
    graph.add_conditional_edges(
        "virtual_fitting",
        should_continue,
        {"continue": "generate_background", "stop": END},
    )
    graph.add_conditional_edges(
        "generate_background",
        should_continue,
        {"continue": "generate_caption", "stop": END},
    )
    graph.add_conditional_edges(
        "generate_caption",
        should_continue,
        {"continue": "generate_html", "stop": END},
    )
    graph.add_conditional_edges(
        "generate_html",
        should_continue,
        {"continue": "save_image", "stop": END},
    )
    graph.add_edge("save_image", END)

    return graph.compile()


# 싱글톤
_pipeline_graph = None

def get_pipeline_graph():
    global _pipeline_graph
    if _pipeline_graph is None:
        _pipeline_graph = build_pipeline_graph()
    return _pipeline_graph
