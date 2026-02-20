"""
광고 카피 생성 서비스
GPT-5를 사용하여 인스타그램 광고 카피를 생성하고 HTML 템플릿과 결합
"""
import os
import json
from typing import Dict, Optional
from openai import OpenAI
from datetime import datetime

from app.templates.ad_templates import AD_TEMPLATES
from config import settings  # ⭐ 추가!

def select_template(style_tags: list) -> str:
    """스타일 태그 기반 템플릿 선택"""
    # 스타일 태그를 소문자로 변환
    tags_lower = [tag.lower() if isinstance(tag, str) else "" for tag in style_tags]
    
    # retro 템플릿 키워드
    retro_keywords = ['빈티지', '레트로', '클래식', '앤티크', '옛날', 'vintage', 'retro', 'Y2K', '페스티벌']
    if any(keyword in tag for tag in tags_lower for keyword in retro_keywords):
        return 'retro'  # ← vintage → retro
    
    # romantic 템플릿 키워드
    romantic_keywords = ['로맨틱', '페미닌', '우아한', '드레스', '원피스', 'romantic', 'elegant', 'feminine']
    if any(keyword in tag for tag in tags_lower for keyword in romantic_keywords):
        return 'romantic'  # ← 추가!
    
    # 기본: resort
    return 'resort'  # ← minimal → resort

class AdGenerator:
    """광고 카피 생성 및 HTML 생성"""
    
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        # ⭐ config.settings에서 API 키 가져오기
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in settings")
        
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,  # ⭐ os.getenv 대신 settings 사용
            timeout=30.0
        )
        self.model = "gpt-5-chat-latest"  # ✅ GPT-5 최신 모델!
    
    def _build_prompt(
        self, 
        vision_result: Dict,
        template_name: str,
        caption: Optional[str] = None,
        user_request: Optional[str] = None,
        ad_inputs: Optional[Dict] = None
    ) -> str:
        """GPT-5 Few-shot 프롬프트 생성"""
        
        # 템플릿별 스타일 가이드
        style_guides = {
            "resort": """매거진 리조트 스타일: 밝고 깔끔하며 세련된 느낌. 세리프 폰트로 우아하고 고급스럽게. 
        여유롭고 경쾌한 톤. "여유", "휴가", "산뜻함", "리조트" 등의 키워드 사용.
        예: "블루 린넨의 여유", "화이트 셔츠의 산뜻함"
        """,
            
            "retro": """Y2K 페스티벌 레트로: 밝고 경쾌하며 트렌디한 느낌. 팝아트 스타일, 대담하고 재미있게. 
        레트로 감성이지만 현대적. "빈티지", "클래식", "레트로", "페스티벌" 등의 키워드. 대문자 headline 가능.
        예: "VINTAGE VIBES", "빈티지 코트의 클래식"
        """,
            
            "romantic": """베이지 골드 로맨틱: 우아하고 청순하며 깨끗한 느낌. 금색 글리터 느낌의 고급스러움. 
        부드럽고 페미닌한 톤. "우아함", "로맨틱", "드림", "엘레강스" 등의 키워드.
        예: "골드 드레스의 우아함", "로맨틱 엘레강스"
        """
        }
        
        template_info = AD_TEMPLATES[template_name]
        style_guide = style_guides.get(template_name, style_guides["resort"])
        
        # Few-shot 예시
        examples = self._get_few_shot_examples(template_name)
        
        # ✨ 캡션 섹션 (있을 경우만)
        caption_section = ""
        if caption:
            caption_section = f"""
[확정된 광고 캡션]
{caption}

⚠️ 위 캡션은 이미 확정된 것입니다. 이 캡션을 그대로 "caption" 필드에 사용하세요.
"""

        ad_inputs_section = ""
        if ad_inputs:
            requirements = []
            if ad_inputs.get('discount'):
                requirements.append(f"할인율: {ad_inputs['discount']}")
            if ad_inputs.get('period'):
                requirements.append(f"기간: {ad_inputs['period']}")
            if ad_inputs.get('brand'):
                requirements.append(f"브랜드명: {ad_inputs['brand']}")
            if ad_inputs.get('keywords'):
                kw = ', '.join(ad_inputs['keywords']) if isinstance(ad_inputs['keywords'], list) else ad_inputs['keywords']
                requirements.append(f"키워드: {kw}")
            if ad_inputs.get('must_include'):
                requirements.append(f"필수 포함: {ad_inputs['must_include']}")
            
            if requirements:
                ad_inputs_section = f"""
    [사용자 지정 광고 정보]
    {chr(10).join(f"- {req}" for req in requirements)}

    ⚠️ 위 정보를 반드시 JSON에 반영하세요. 특히 discount, brand, period는 사용자가 입력한 값 그대로 사용!
    """
        
        prompt = f"""당신은 인스타그램 광고 전문 카피라이터입니다.

[템플릿 스타일: {template_info['name']}]
{style_guide}

[상품 정보]
- 카테고리: {vision_result.get('category', 'N/A')}
- 서브 카테고리: {vision_result.get('sub_category', 'N/A')}
- 색상: {vision_result.get('color', 'N/A')}
- 소재: {vision_result.get('material', 'N/A')}
- 핏: {vision_result.get('fit', 'N/A')}
- 스타일: {', '.join(vision_result.get('style_tags', []))}

{caption_section}
{ad_inputs_section}
{f"[사용자 요청사항]\n{user_request}\n" if user_request else ""}

[Few-shot 예시]
{examples}

위 정보를 바탕으로 인스타그램 광고 카피를 생성하세요.

⚠️ 중요: 
1. 반드시 한글로만 작성하세요 (인코딩 깨짐 방지)
2. 반드시 아래 JSON 형식으로만 응답하세요
3. 다른 텍스트는 포함하지 마세요

{{
  "headline": "메인 헤드라인 (20자 이내)",
  "subtext": "부제 또는 서브 텍스트 (15자 이내, 선택)",
  "discount": "할인율 (예: 70% OFF)",
  "period": "기간 (MM.DD - MM.DD 형식)",
  "brand": "브랜드명 또는 이벤트명 (10자 이내)",
  "event_name": "이벤트명 (bold 템플릿용, 선택)",
  "caption": "{caption if caption else '인스타그램 캡션 (이모지 포함, 50자 이내)'}"
}}"""
        
        return prompt
    
    def _get_few_shot_examples(self, template_name: str) -> str:
        """템플릿별 Few-shot 예시 반환"""
        examples = {
            "resort": """예시 1 (리조트 블라우스):
    입력: 카테고리=상의, 색상=블루, 스타일=리조트
    출력:
    {
    "headline": "블루 린넨의 여유",
    "subtext": "편안한 휴가를 완성하는",
    "discount": "30% OFF",
    "period": "07.01 - 07.07",
    "brand": "RESORT COLLECTION",
    "caption": "🏖️ 시원한 블루 컬러로 완성하는 리조트 룩"
    }

    예시 2 (화이트 셔츠):
    입력: 카테고리=상의, 색상=화이트, 스타일=깔끔
    출력:
    {
    "headline": "화이트 셔츠의 산뜻함",
    "subtext": "밝은 하루를 시작하는",
    "discount": "40% OFF",
    "period": "주말특가",
    "brand": "FRESH STYLE",
    "caption": "☀️ 깔끔하게 빛나는 여름 화이트 셔츠"
    }

    예시 3 (베이지 팬츠):
    입력: 카테고리=하의, 색상=베이지, 스타일=리조트
    출력:
    {
    "headline": "베이지 팬츠의 우아함",
    "subtext": "리조트 룩의 완성",
    "discount": "35% OFF",
    "period": "한정수량",
    "brand": "VACATION MODE",
    "caption": "🌴 편안하면서도 세련된 베이지 컬러"
    }""",

            "retro": """예시 1 (빈티지 코트):
    입력: 카테고리=아우터, 색상=브라운, 스타일=빈티지
    출력:
    {
    "headline": "VINTAGE CLASSIC",
    "subtext": "시간이 만든 멋",
    "discount": "35% OFF",
    "period": "한정수량",
    "brand": "RETRO VIBE",
    "caption": "📼 클래식한 빈티지 스타일로 완성하는 가을"
    }

    예시 2 (레트로 니트):
    입력: 카테고리=상의, 색상=브라운, 스타일=레트로
    출력:
    {
    "headline": "브라운 니트의 따뜻함",
    "subtext": "옛 감성을 담은",
    "discount": "25% OFF",
    "period": "2주간",
    "brand": "NEPA STYLE",
    "caption": "🍂 따뜻한 추억을 만드는 레트로 니트"
    }

    예시 3 (데님 재킷):
    입력: 카테고리=아우터, 색상=블루, 스타일=Y2K
    출력:
    {
    "headline": "DENIM FESTIVAL",
    "subtext": "Y2K의 귀환",
    "discount": "30% OFF",
    "period": "주말한정",
    "brand": "FESTIVAL MODE",
    "caption": "✨ 페스티벌 감성 가득한 데님 스타일"
    }""",

            "romantic": """예시 1 (골드 드레스):
    입력: 카테고리=원피스, 색상=골드, 스타일=로맨틱
    출력:
    {
    "headline": "골드 드레스의 우아함",
    "subtext": "꿈같은 순간을 위한",
    "discount": "50% OFF",
    "period": "봄맞이",
    "brand": "ROMANTIC DREAM",
    "caption": "✨ 우아하고 로맨틱한 골드 드레스"
    }

    예시 2 (레이스 원피스):
    입력: 카테고리=원피스, 색상=베이지, 스타일=엘레강스
    출력:
    {
    "headline": "레이스의 로맨스",
    "subtext": "화려하게 빛나는",
    "discount": "45% OFF",
    "period": "5일간",
    "brand": "ELEGANT STYLE",
    "caption": "💕 섬세한 레이스 디테일이 돋보이는 원피스"
    }

    예시 3 (베이지 원피스):
    입력: 카테고리=원피스, 색상=베이지, 스타일=청순
    출력:
    {
    "headline": "베이지 엘레강스",
    "subtext": "청순한 아름다움",
    "discount": "40% OFF",
    "period": "한정기간",
    "brand": "STONEHENGE",
    "caption": "🌸 부드러운 베이지로 완성하는 로맨틱 룩"
    }"""
        }
        
        return examples.get(template_name, examples["resort"])  # minimal → resort

    
    def generate_ad_copy(
        self, 
        vision_result: Dict,
        user_request: Optional[str] = None,
        caption: Optional[str] = None  # ✨ 추가
    ) -> Dict:
        """
        GPT-4로 광고 카피 생성
        
        Args:
            vision_result: Vision AI 분석 결과
            user_request: 사용자 추가 요청
            caption: 확정된 캡션 (AdCaption에서 가져온 값)
        
        Returns:
            광고 카피 dict
        """
        
        # 1. 템플릿 선택
        style_tags = vision_result.get('style_tags', [])
        template_name = select_template(style_tags)
        
        # 2. 프롬프트 생성
        prompt = self._build_prompt(vision_result, template_name, caption, user_request)
        
        # 3. GPT-4 호출
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 인스타그램 광고 전문 카피라이터입니다.

⚠️ CRITICAL - 인코딩 규칙:
1. 반드시 UTF-8 인코딩으로 한글 작성
2. 모든 텍스트는 순수 한글 문자만 사용
3. 이스케이프 시퀀스나 특수 인코딩 사용 금지
4. JSON 응답에서 한글이 깨지지 않도록 주의

예시: "베이지의 따뜻함" (O), "string" (X)

반드시 JSON 형식으로만 응답합니다."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500,  # ✨ max_completion_tokens → max_tokens
                timeout=30.0,  # ✨ 타임아웃 추가
                response_format={"type": "json_object"}  # JSON 모드 강제
            )
            
            # 4. 응답 파싱
            content = response.choices[0].message.content
            
            # ✨ UTF-8 인코딩 명시적 처리
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            ad_copy = json.loads(content)
            
            # ✨ 한글 인코딩 검증
            headline = ad_copy.get('headline', '')
            if headline:
                # 한글이 제대로 있는지 확인
                korean_chars = sum(1 for c in headline if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
                if korean_chars == 0:
                    print(f"⚠️ 한글 인코딩 문제 감지: {headline}")
                    # UTF-8로 재인코딩 시도
                    try:
                        headline_bytes = headline.encode('latin-1')
                        headline = headline_bytes.decode('utf-8')
                        ad_copy['headline'] = headline
                        print(f"✅ 한글 인코딩 복구: {headline}")
                    except:
                        print(f"❌ 한글 인코딩 복구 실패")
                else:
                    print(f"✅ 한글 인코딩 정상: {headline} ({korean_chars}자)")
            
            # 5. ✨ 캡션이 제공된 경우 강제로 사용
            if caption:
                ad_copy['caption'] = caption
            
            # 6. 템플릿 이름 추가
            ad_copy['template_used'] = template_name
            
            return ad_copy
            
        except Exception as e:
            print(f"❌ GPT-4 API Error: {e}")
            # 폴백: 기본 카피 반환
            return self._get_fallback_copy(vision_result, template_name, caption)
    
    def _get_fallback_copy(
        self, 
        vision_result: Dict, 
        template_name: str,
        caption: Optional[str] = None  # ✨ 추가
    ) -> Dict:
        """
        GPT-4 실패 시 기본 카피 반환
        """
        category = vision_result.get('category', '상품')
        fallback_caption = caption if caption else f"🎉 {category} 특가 진행 중!"
        
        return {
            "headline": f"{category} 특가",
            "subtext": "지금 바로",
            "discount": "50% OFF",
            "period": "한정 기간",
            "brand": "SPECIAL SALE",
            "event_name": "특별 이벤트",
            "caption": fallback_caption,
            "template_used": template_name
        }
    
    def generate_html(
        self,
        vision_result: Dict,
        image_url: str,
        caption: Optional[str] = None,  # ✨ 추가
        user_request: Optional[str] = None
    ) -> Dict:
        """
        광고 카피 생성 + HTML 템플릿 결합
        
        Args:
            vision_result: Vision AI 분석 결과
            image_url: 생성된 모델 이미지 URL
            caption: 확정된 캡션 (선택, AdCaption에서 가져온 값)
            user_request: 사용자 추가 요청
        
        Returns:
            {
                'html': HTML 문자열,
                'ad_copy': 광고 카피 dict,
                'template_used': 템플릿 이름
            }
        """
        
        # 1. 광고 카피 생성
        ad_copy = self.generate_ad_copy(vision_result, user_request, caption)  # ✨ caption 전달
        template_name = ad_copy['template_used']
        
        # 2. 템플릿 HTML 가져오기
        template_html = AD_TEMPLATES[template_name]['html']
        
        # 3. 변수 치환
        replacements = {
            "{{IMAGE_URL}}": image_url,
            "{{HEADLINE}}": ad_copy.get('headline', '특가 이벤트'),
            "{{SUBTEXT}}": ad_copy.get('subtext', ''),
            "{{DISCOUNT}}": ad_copy.get('discount', '50% OFF'),
            "{{PERIOD}}": ad_copy.get('period', '한정 기간'),
            "{{BRAND}}": ad_copy.get('brand', 'SALE'),
            "{{EVENT_NAME}}": ad_copy.get('event_name', '특별 이벤트')
        }
        
        html = template_html
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
        
        return {
            'html': html,
            'ad_copy': ad_copy,
            'template_used': template_name
        }
    
    def generate_html_with_template(
        self,
        vision_result: Dict,
        image_url: str,
        template_name: str,  # ✨ 템플릿 명시
        caption: Optional[str] = None,
        user_request: Optional[str] = None,
        ad_inputs: Optional[Dict] = None
    ) -> Dict:
        """
        ✨ NEW: 특정 템플릿으로 광고 생성
        
        3개 템플릿 모두 생성할 때 사용
        
        Args:
            vision_result: Vision AI 분석 결과
            image_url: 생성된 모델 이미지 URL
            template_name: 사용할 템플릿 (minimal, bold, vintage)
            caption: 확정된 캡션
            user_request: 사용자 추가 요청
        
        Returns:
            {
                'html': HTML 문자열,
                'ad_copy': 광고 카피 dict,
                'template_used': 템플릿 이름
            }
        """
        
        # 1. 템플릿 유효성 검사
        if template_name not in AD_TEMPLATES:
            raise ValueError(f"Invalid template: {template_name}")
        
        # 2. 해당 템플릿으로 광고 카피 생성
        ad_copy = self.generate_ad_copy_for_template(
            vision_result,
            template_name,
            caption,
            user_request,
            ad_inputs
        )
        
        if ad_inputs:
            print(f"📝 사용자 광고 정보:")
            if ad_inputs.get('discount'):
                print(f"   - 할인율: {ad_inputs['discount']}")
                ad_copy['discount'] = ad_inputs['discount']
            if ad_inputs.get('brand'):
                print(f"   - 브랜드: {ad_inputs['brand']}")
                ad_copy['brand'] = ad_inputs['brand']
            if ad_inputs.get('period'):
                print(f"   - 기간: {ad_inputs['period']}")
                ad_copy['period'] = ad_inputs['period']

        # 3. 템플릿 HTML 가져오기
        template_html = AD_TEMPLATES[template_name]['html']
        
        # 4. 변수 치환
        replacements = {
            "{{IMAGE_URL}}": image_url,
            "{{HEADLINE}}": ad_copy.get('headline', '특가 이벤트'),
            "{{SUBTEXT}}": ad_copy.get('subtext', ''),
            "{{DISCOUNT}}": ad_copy.get('discount', '50% OFF'),
            "{{PERIOD}}": ad_copy.get('period', '한정 기간'),
            "{{BRAND}}": ad_copy.get('brand', 'SALE'),
            "{{EVENT_NAME}}": ad_copy.get('event_name', '특별 이벤트')
        }
        
        html = template_html
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
        
        return {
            'html': html,
            'ad_copy': ad_copy,
            'template_used': template_name
        }
    
    def generate_ad_copy_for_template(
        self,
        vision_result: Dict,
        template_name: str,  # ✨ 템플릿 고정
        caption: Optional[str] = None,
        user_request: Optional[str] = None,
        ad_inputs: Optional[Dict] = None
    ) -> Dict:
        """
        ✨ NEW: 특정 템플릿에 맞는 광고 카피 생성
        
        Args:
            vision_result: Vision AI 분석 결과
            template_name: 사용할 템플릿
            caption: 확정된 캡션
            user_request: 사용자 추가 요청
        
        Returns:
            광고 카피 dict
        """
        
        # 프롬프트 생성 (템플릿 고정)
        prompt = self._build_prompt(vision_result, template_name, caption, user_request, ad_inputs)
        
        # GPT 호출
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 인스타그램 광고 전문 카피라이터입니다.

⚠️ CRITICAL - 인코딩 규칙:
1. 반드시 UTF-8 인코딩으로 한글 작성
2. 모든 텍스트는 순수 한글 문자만 사용
3. 이스케이프 시퀀스나 특수 인코딩 사용 금지
4. JSON 응답에서 한글이 깨지지 않도록 주의

예시: "베이지의 따뜻함" (O), "string" (X)

반드시 JSON 형식으로만 응답합니다."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=30.0,
                response_format={"type": "json_object"}
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # UTF-8 인코딩 명시적 처리
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            ad_copy = json.loads(content)
            
            # 한글 인코딩 검증
            headline = ad_copy.get('headline', '')
            if headline:
                korean_chars = sum(1 for c in headline if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
                if korean_chars == 0:
                    print(f"⚠️ [{template_name}] 한글 인코딩 문제 감지: {headline}")
                    try:
                        headline_bytes = headline.encode('latin-1')
                        headline = headline_bytes.decode('utf-8')
                        ad_copy['headline'] = headline
                        print(f"✅ [{template_name}] 한글 인코딩 복구: {headline}")
                    except:
                        print(f"❌ [{template_name}] 한글 인코딩 복구 실패")
                else:
                    print(f"✅ [{template_name}] 한글 인코딩 정상: {headline}")
            
            # 캡션이 제공된 경우 강제로 사용
            if caption:
                ad_copy['caption'] = caption

            if ad_inputs and ad_inputs.get('must_include'):
                must_include = ad_inputs['must_include']
                current_headline = ad_copy.get('headline', '')
                
                # headline에 필수 문구가 없으면 추가
                if must_include not in current_headline:
                    ad_copy['headline'] = f"{current_headline} - {must_include}"
                    print(f"✅ 필수 문구 추가: {ad_copy['headline']}")
            
            if ad_inputs and ad_inputs.get('period'):
                period = ad_inputs['period']
                current_headline = ad_copy.get('headline', '')
                
                # 기간이 없으면 추가
                if period not in current_headline:
                    ad_copy['headline'] = f"{current_headline} ({period})"
                    print(f"✅ 기간 추가: {ad_copy['headline']}")

            # 템플릿 이름 추가
            ad_copy['template_used'] = template_name
            
            return ad_copy
            
        except Exception as e:
            print(f"❌ [{template_name}] GPT API Error: {e}")
            return self._get_fallback_copy(vision_result, template_name, caption)

# 테스트용
if __name__ == "__main__":
    # 테스트
    generator = AdGenerator()
    
    test_vision_result = {
        "category": "아우터",
        "sub_category": "코트",
        "material": "울",
        "fit": "오버사이즈",
        "color": "블랙",
        "style_tags": ["미니멀", "모던"]
    }
    
    test_image_url = "https://storage.googleapis.com/test/model.jpg"
    test_caption = "클래식한 블랙 울 코트로 겨울 스타일을 완성하세요 ❄️"
    
    print("=" * 50)
    print("광고 카피 생성 테스트")
    print("=" * 50)
    
    result = generator.generate_html(
        vision_result=test_vision_result,
        image_url=test_image_url,
        caption=test_caption,  # ✨ 캡션 추가
        user_request="세련된 느낌으로"
    )
    
    print(f"\n✅ 템플릿: {result['template_used']}")
    print(f"\n광고 카피:")
    print(json.dumps(result['ad_copy'], indent=2, ensure_ascii=False))
    print(f"\n✅ HTML 생성 완료 (길이: {len(result['html'])} 글자)")