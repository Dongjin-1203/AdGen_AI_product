"""
스타일 자동 매칭 유틸리티
Vision AI 스타일 태그 → 광고 스타일 자동 선택
"""
from typing import List


def auto_match_style(vision_tags: List[str], category: str = None) -> str:
    """
    Vision AI 스타일 태그로 광고 스타일 자동 선택
    
    Args:
        vision_tags: Vision AI가 분석한 스타일 태그 리스트
        category: 상품 카테고리 (optional)
    
    Returns:
        광고 스타일 (minimal, bold, vintage, lookbook)
    """
    
    # 태그를 소문자로 변환하여 문자열로 합침
    tags_text = ' '.join(vision_tags).lower() if vision_tags else ''
    
    # 스타일별 키워드 매핑
    style_keywords = {
        'vintage': [
            '빈티지', '레트로', '클래식', '앤티크', '옛날',
            'vintage', 'retro', 'classic', 'antique'
        ],
        'bold': [
            '대담한', '강렬한', '임팩트', '화려한', '세일', '할인',
            'bold', 'strong', 'impact', 'sale', 'vivid'
        ],
        'lookbook': [
            '룩북', '스트릿', '캐주얼', '트렌디', '영',
            'lookbook', 'street', 'casual', 'trendy', 'young'
        ],
        'minimal': [
            '미니멀', '모던', '심플', '깔끔', '현대적', '세련된',
            'minimal', 'modern', 'simple', 'clean', 'contemporary'
        ],
    }
    
    # 각 스타일별 매칭 점수 계산
    scores = {}
    for style, keywords in style_keywords.items():
        score = sum(1 for keyword in keywords if keyword in tags_text)
        if score > 0:
            scores[style] = score
    
    # 가장 높은 점수의 스타일 선택
    if scores:
        selected_style = max(scores, key=scores.get)
        return selected_style
    
    # 매칭되는 키워드가 없으면 카테고리 기반 기본값
    if category:
        category_defaults = {
            '원피스': 'romantic',
            '드레스': 'romantic',
            '블라우스': 'minimal',
            '셔츠': 'minimal',
            '티셔츠': 'lookbook',
            '아우터': 'bold',
            '코트': 'bold',
            '재킷': 'bold',
            '팬츠': 'lookbook',
            '스커트': 'minimal',
        }
        
        for key, style in category_defaults.items():
            if key in category:
                return style
    
    # 최종 기본값
    return 'minimal'


# 테스트
if __name__ == "__main__":
    # 테스트 케이스
    test_cases = [
        (["빈티지", "레트로"], "상의", "vintage"),
        (["미니멀", "모던"], "블라우스", "minimal"),
        (["대담한", "강렬한"], "아우터", "bold"),
        (["캐주얼", "트렌디"], "티셔츠", "lookbook"),
        ([], "원피스", "romantic"),  # 태그 없을 때 카테고리 기반
        ([], "블라우스", "minimal"),  # 태그 없을 때 카테고리 기반
    ]
    
    print("=== 스타일 자동 매칭 테스트 ===\n")
    for tags, category, expected in test_cases:
        result = auto_match_style(tags, category)
        status = "✅" if result == expected else "❌"
        print(f"{status} Tags: {tags}, Category: {category}")
        print(f"   Expected: {expected}, Got: {result}\n")