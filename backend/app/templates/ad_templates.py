"""
인스타그램 광고 템플릿 라이브러리
1080×1080px 정사각형 포맷
오버레이 방식: 배경 이미지 위에 텍스트 배치
"""

AD_TEMPLATES = {
    "minimal": {
        "name": "Minimal Overlay",
        "description": "배경 이미지 위에 깔끔한 텍스트 오버레이",
        "colors": ["#FFFFFF", "#000000", "#F5F5F5"],
        "best_for": ["미니멀", "모던", "심플", "깔끔", "현대적"],
        "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: 1080px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', sans-serif;
        }
        .background-image {
            width: 95%;
            height: 95%;
            object-fit: contain;
            position: absolute;
            top: 2.5%;
            left: 2.5%;
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to bottom,
                rgba(0,0,0,0.3) 0%,
                rgba(0,0,0,0) 50%,
                rgba(0,0,0,0.5) 100%
            );
        }
        .brand {
            position: absolute;
            top: 60px;
            left: 60px;
            font-size: 22px;
            color: white;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-weight: 300;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        }
        .headline {
            position: absolute;
            bottom: 200px;
            left: 60px;
            right: 60px;
            font-size: 64px;
            font-weight: 700;
            color: white;
            line-height: 1.2;
            letter-spacing: -2px;
            text-shadow: 3px 3px 12px rgba(0,0,0,0.8);
        }
        .discount {
            position: absolute;
            bottom: 60px;
            right: 60px;
            font-size: 80px;
            font-weight: 900;
            color: #FF4757;
            background: white;
            padding: 25px 50px;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }
        .period {
            position: absolute;
            bottom: 70px;
            left: 60px;
            font-size: 20px;
            color: white;
            letter-spacing: 2px;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="brand">{{BRAND}}</div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="period">{{PERIOD}}</div>
    <div class="discount">{{DISCOUNT}}</div>
</body>
</html>"""
    },
    
    "bold": {
        "name": "Bold Impact Overlay",
        "description": "강렬한 그라데이션 배경에 임팩트 있는 텍스트",
        "colors": ["#E74C3C", "#FFFFFF", "#2C3E50"],
        "best_for": ["대담한", "강렬한", "임팩트", "세일", "할인"],
        "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: 1080px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', sans-serif;
        }
        .background-image {
            width: 95%;
            height: 95%;
            object-fit: contain;
            position: absolute;
            top: 2.5%;
            left: 2.5%;
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                135deg,
                rgba(231, 76, 60, 0.7) 0%,
                rgba(231, 76, 60, 0.3) 50%,
                rgba(44, 62, 80, 0.8) 100%
            );
        }
        .headline {
            position: absolute;
            top: 80px;
            left: 60px;
            right: 60px;
            font-size: 80px;
            font-weight: 900;
            color: white;
            line-height: 1.1;
            text-transform: uppercase;
            letter-spacing: -3px;
            text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        }
        .event-name {
            position: absolute;
            bottom: 180px;
            left: 60px;
            font-size: 32px;
            font-weight: 600;
            color: white;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        }
        .discount-badge {
            position: absolute;
            bottom: 60px;
            right: 60px;
            background: white;
            color: #E74C3C;
            padding: 30px 60px;
            border-radius: 20px;
            font-size: 72px;
            font-weight: 900;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="headline">{{HEADLINE}}</div>
    <div class="event-name">{{EVENT_NAME}}</div>
    <div class="discount-badge">{{DISCOUNT}}</div>
</body>
</html>"""
    },
    
    "vintage": {
        "name": "Vintage Overlay",
        "description": "세피아 필터와 레트로 타이포 오버레이",
        "colors": ["#D4A574", "#8B7355", "#F5E6D3"],
        "best_for": ["빈티지", "레트로", "클래식", "앤티크", "옛날"],
        "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: 1080px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            font-family: Georgia, 'Playfair Display', serif;
        }
        .background-image {
            width: 95%;
            height: 95%;
            object-fit: contain;
            position: absolute;
            top: 2.5%;
            left: 2.5%;
            filter: sepia(40%) contrast(95%);
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to bottom,
                rgba(213, 165, 116, 0.4) 0%,
                rgba(213, 165, 116, 0.1) 50%,
                rgba(93, 78, 55, 0.6) 100%
            );
        }
        .border-frame {
            position: absolute;
            top: 40px;
            left: 40px;
            right: 40px;
            bottom: 40px;
            border: 8px solid rgba(139, 115, 85, 0.7);
            pointer-events: none;
        }
        .headline {
            position: absolute;
            bottom: 200px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 68px;
            font-weight: 700;
            color: #F5E6D3;
            text-shadow: 3px 3px 10px rgba(93, 78, 55, 0.9);
            letter-spacing: 2px;
        }
        .discount {
            position: absolute;
            bottom: 100px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 72px;
            color: #D4A574;
            font-weight: 700;
            text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
        }
        .period {
            position: absolute;
            bottom: 50px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 22px;
            color: #F5E6D3;
            letter-spacing: 3px;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="border-frame"></div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="discount">{{DISCOUNT}}</div>
    <div class="period">{{PERIOD}}</div>
</body>
</html>"""
    },
    
    "lookbook": {
        "name": "Lookbook Style",
        "description": "#LOOK 태그와 제품 라벨이 있는 룩북 스타일",
        "colors": ["#2C3E50", "#FFFFFF", "#FF6B9D"],
        "best_for": ["룩북", "스트릿", "캐주얼", "트렌디", "영"],
        "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            width: 1080px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }
        .background-image {
            width: 95%;
            height: 95%;
            object-fit: contain;
            position: absolute;
            top: 2.5%;
            left: 2.5%;
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to bottom,
                rgba(44, 62, 80, 0.4) 0%,
                rgba(44, 62, 80, 0) 40%,
                rgba(44, 62, 80, 0) 60%,
                rgba(44, 62, 80, 0.6) 100%
            );
        }
        .hashtag {
            position: absolute;
            top: 60px;
            right: 60px;
            font-size: 80px;
            font-weight: 900;
            color: #FF6B9D;
            text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
            letter-spacing: 2px;
        }
        .brand {
            position: absolute;
            bottom: 60px;
            left: 60px;
            font-size: 56px;
            font-weight: 700;
            color: white;
            letter-spacing: 3px;
            text-shadow: 3px 3px 12px rgba(0,0,0,0.8);
        }
        .headline {
            position: absolute;
            bottom: 150px;
            left: 60px;
            font-size: 32px;
            font-weight: 300;
            color: white;
            letter-spacing: 1px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        }
        .discount {
            position: absolute;
            top: 60px;
            left: 60px;
            font-size: 48px;
            font-weight: 900;
            color: white;
            background: #FF6B9D;
            padding: 20px 40px;
            border-radius: 15px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.4);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="hashtag">#LOOK</div>
    <div class="discount">{{DISCOUNT}}</div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="brand">{{BRAND}}</div>
</body>
</html>"""
    }
}


def get_template(template_name: str) -> dict:
    """
    템플릿 가져오기
    
    Args:
        template_name: 'minimal', 'bold', 'vintage', 'lookbook'
    
    Returns:
        템플릿 정보 dict
    """
    return AD_TEMPLATES.get(template_name, AD_TEMPLATES["minimal"])


def list_templates() -> list:
    """
    사용 가능한 모든 템플릿 목록
    
    Returns:
        템플릿 이름 리스트
    """
    return list(AD_TEMPLATES.keys())