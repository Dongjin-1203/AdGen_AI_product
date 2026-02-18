"""
파이프라인 단계별 검증 로직
pre_check: 노드 진입 전 검증
post_check: 노드 완료 후 결과 검증
"""
from typing import Optional, Tuple


# ===== 카테고리 충돌 감지 =====

# 상품 카테고리 → 착용 불가 모델 카테고리 매핑
CATEGORY_CONFLICT_MAP = {
    "상의": ["원피스", "드레스", "점프수트"],
    "하의": ["원피스", "드레스", "점프수트"],
    "아우터": [],   # 아우터는 대부분 착용 가능
}

# 모델 이미지 스타일 → 착의 카테고리 추정
# K-Fashion 모델 파일명 컨벤션 기반
MODEL_WEARING_CATEGORY = {
    "resort": "상의",       # 리조트 모델 = 일반 상의 착용
    "retro": "상의",        # 레트로 모델 = 일반 상의 착용
    "romantic": "원피스",   # 로맨틱 모델 = 원피스/드레스 착용
}


def check_vton_category_conflict(
    product_category: Optional[str],
    style: str,
) -> Tuple[bool, Optional[str]]:
    """
    IDM-VTON 카테고리 충돌 감지

    Args:
        product_category: 상품 카테고리 (Vision AI 분석 결과)
        style: 선택된 스타일 (resort/retro/romantic)

    Returns:
        (is_conflict, error_message)
        is_conflict=True → 파이프라인 중단
    """
    if not product_category:
        # 카테고리 정보 없으면 통과 (경고만)
        return False, None

    model_wearing = MODEL_WEARING_CATEGORY.get(style, "상의")
    conflict_categories = CATEGORY_CONFLICT_MAP.get(product_category, [])

    if model_wearing in conflict_categories:
        error_msg = (
            f"카테고리 충돌 감지: '{product_category}' 상품은 "
            f"'{style}' 스타일 모델({model_wearing} 착용)과 함께 사용할 수 없습니다. "
            f"resort 또는 retro 스타일을 선택해주세요."
        )
        return True, error_msg

    return False, None


# ===== 이미지 검증 =====

def validate_image_url(url: Optional[str], step_name: str) -> Tuple[bool, Optional[str]]:
    """이미지 URL 존재 여부 검증"""
    if not url:
        return False, f"{step_name}: 이미지 URL이 없습니다."
    if not url.startswith("https://"):
        return False, f"{step_name}: 유효하지 않은 이미지 URL입니다."
    return True, None


def validate_text_output(text: Optional[str], step_name: str, min_length: int = 5) -> Tuple[bool, Optional[str]]:
    """텍스트 출력 검증 (캡션, HTML 등)"""
    if not text:
        return False, f"{step_name}: 결과가 비어있습니다."
    if len(text) < min_length:
        return False, f"{step_name}: 결과가 너무 짧습니다. (최소 {min_length}자)"
    return True, None


# ===== 단계별 검증 함수 모음 =====

def pre_check_select_image(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 1: 상품 이미지 선택 전 검증"""
    if not state.get("content_id"):
        return False, "content_id가 없습니다."
    return True, None


def post_check_select_image(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 1: 상품 이미지 선택 후 검증"""
    return validate_image_url(state.get("product_image_url"), "이미지 선택")


def pre_check_remove_background(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 2: 배경 제거 전 검증"""
    return validate_image_url(state.get("product_image_url"), "배경 제거")


def post_check_remove_background(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 2: 배경 제거 후 검증"""
    return validate_image_url(state.get("removed_bg_url"), "배경 제거 결과")


def pre_check_virtual_fitting(state: dict) -> Tuple[bool, Optional[str]]:
    """
    Node 3: 가상 피팅 전 검증
    핵심: 카테고리 충돌 감지
    """
    # 배경 제거 이미지 확인
    ok, err = validate_image_url(state.get("removed_bg_url"), "가상 피팅 입력")
    if not ok:
        return False, err

    # 카테고리 충돌 감지
    is_conflict, conflict_msg = check_vton_category_conflict(
        product_category=state.get("product_category"),
        style=state.get("style", "resort"),
    )
    if is_conflict:
        return False, conflict_msg

    return True, None


def post_check_virtual_fitting(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 3: 가상 피팅 후 검증"""
    return validate_image_url(state.get("fitted_image_url"), "가상 피팅 결과")


def pre_check_generate_background(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 4: 배경 생성 전 검증"""
    return validate_image_url(state.get("fitted_image_url"), "배경 생성 입력")


def post_check_generate_background(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 4: 배경 생성 후 검증"""
    return validate_image_url(state.get("background_image_url"), "배경 생성 결과")


def pre_check_generate_caption(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 5: 캡션 생성 전 검증"""
    return validate_image_url(state.get("background_image_url"), "캡션 생성 입력")


def post_check_generate_caption(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 5: 캡션 생성 후 검증"""
    return validate_text_output(state.get("caption"), "캡션 생성", min_length=10)


def pre_check_generate_html(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 6: HTML 생성 전 검증"""
    ok, err = validate_text_output(state.get("caption"), "HTML 생성 입력")
    return ok, err


def post_check_generate_html(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 6: HTML 생성 후 검증"""
    return validate_text_output(state.get("html_content"), "HTML 생성", min_length=100)


def pre_check_save_image(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 7: 이미지 저장 전 검증"""
    return validate_text_output(state.get("html_content"), "이미지 저장 입력", min_length=100)


def post_check_save_image(state: dict) -> Tuple[bool, Optional[str]]:
    """Node 7: 이미지 저장 후 검증"""
    return validate_image_url(state.get("final_image_url"), "이미지 저장 결과")


# ===== 검증 함수 레지스트리 =====
PRE_CHECKS = {
    "select_image": pre_check_select_image,
    "remove_background": pre_check_remove_background,
    "virtual_fitting": pre_check_virtual_fitting,
    "generate_background": pre_check_generate_background,
    "generate_caption": pre_check_generate_caption,
    "generate_html": pre_check_generate_html,
    "save_image": pre_check_save_image,
}

POST_CHECKS = {
    "select_image": post_check_select_image,
    "remove_background": post_check_remove_background,
    "virtual_fitting": post_check_virtual_fitting,
    "generate_background": post_check_generate_background,
    "generate_caption": post_check_generate_caption,
    "generate_html": post_check_generate_html,
    "save_image": post_check_save_image,
}
