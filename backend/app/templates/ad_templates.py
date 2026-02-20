"""
인스타그램 광고 템플릿 라이브러리
K-Fashion 모델 컨셉에 최적화된 3가지 템플릿
- resort: 매거진 리조트
- retro: Y2K 페스티벌
- romantic: 베이지 골드 우아함
"""

AD_TEMPLATES = {
    "resort": {
        "name": "Resort Magazine",
        "description": "밝고 깔끔한 매거진 리조트 - 상의/하의 모델",
        "colors": ["#F5E6D3", "#B8956A", "#FFFFFF"],
        "best_for": ["리조트", "매거진", "깔끔한", "고급스러운"],
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
            width: 96%;
            height: 96%;
            object-fit: contain;
            position: absolute;
            top: 2%;
            left: 2%;
            filter: brightness(1.05) saturate(1.1);
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to bottom,
                rgba(245, 230, 211, 0.15) 0%,
                rgba(245, 230, 211, 0) 40%,
                rgba(0, 0, 0, 0.5) 100%
            );
        }
        .brand-box {
            position: absolute;
            top: 50px;
            left: 50px;
            background: rgba(184, 149, 106, 0.9);
            color: white;
            padding: 18px 50px;
            font-family: Georgia, serif;
            font-size: 28px;
            letter-spacing: 10px;
            text-transform: uppercase;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        .headline {
            position: absolute;
            bottom: 200px;
            left: 60px;
            right: 60px;
            font-family: Georgia, 'Playfair Display', serif;
            font-size: 68px;
            font-weight: 700;
            color: white;
            line-height: 1.25;
            letter-spacing: -1px;
            text-shadow: 3px 3px 15px rgba(0,0,0,0.8);
        }
        .period {
            position: absolute;
            bottom: 150px;
            left: 60px;
            font-size: 26px;
            font-weight: 600;
            color: #FFD700;
            letter-spacing: 3px;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
        }
        .discount {
            position: absolute;
            bottom: 60px;
            right: 60px;
            background: white;
            color: #B8956A;
            padding: 25px 50px;
            border-radius: 15px;
            font-size: 72px;
            font-weight: 900;
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="brand-box">{{BRAND}}</div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="period">{{PERIOD}}</div>
    <div class="discount">{{DISCOUNT}}</div>
</body>
</html>"""
    },
    
    "retro": {
        "name": "Retro Festival",
        "description": "밝고 경쾌한 Y2K 레트로 페스티벌 - 상의/하의 모델",
        "colors": ["#FF6B6B", "#4ECDC4", "#FFE66D"],
        "best_for": ["레트로", "페스티벌", "Y2K", "트렌디"],
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
            width: 96%;
            height: 96%;
            object-fit: contain;
            position: absolute;
            top: 2%;
            left: 2%;
            filter: brightness(1.05) contrast(1.05);
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                135deg,
                rgba(255, 230, 109, 0.3) 0%,
                rgba(78, 205, 196, 0.2) 50%,
                rgba(255, 107, 107, 0.4) 100%
            );
        }
        .retro-pattern {
            position: absolute;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(255, 255, 255, 0.03) 10px,
                rgba(255, 255, 255, 0.03) 20px
            );
            pointer-events: none;
        }
        .brand {
            position: absolute;
            top: 60px;
            left: 60px;
            font-size: 48px;
            font-weight: 900;
            color: #FF6B6B;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 
                3px 3px 0px #FFE66D,
                6px 6px 0px rgba(0,0,0,0.2);
            font-style: italic;
        }
        .headline {
            position: absolute;
            bottom: 240px;
            left: 60px;
            right: 60px;
            font-size: 76px;
            font-weight: 900;
            color: white;
            line-height: 1.1;
            letter-spacing: -1px;
            text-transform: uppercase;
            text-shadow: 
                4px 4px 0px #FF6B6B,
                8px 8px 0px rgba(0,0,0,0.3);
        }
        .period {
            position: absolute;
            bottom: 180px;
            left: 60px;
            background: #FFE66D;
            color: #2D3436;
            padding: 12px 30px;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: 2px;
            transform: rotate(-2deg);
            box-shadow: 4px 4px 0px rgba(0,0,0,0.2);
        }
        .discount {
            position: absolute;
            bottom: 60px;
            right: 60px;
            background: white;
            color: #FF6B6B;
            padding: 35px 50px;
            border-radius: 50%;
            font-size: 68px;
            font-weight: 900;
            box-shadow: 
                0 0 0 8px #FF6B6B,
                0 0 0 16px white,
                0 0 0 24px #4ECDC4,
                8px 8px 30px rgba(0,0,0,0.3);
            transform: rotate(8deg);
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="retro-pattern"></div>
    <div class="brand">{{BRAND}}</div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="period">{{PERIOD}}</div>
    <div class="discount">{{DISCOUNT}}</div>
</body>
</html>"""
    },
    
    "romantic": {
        "name": "Romantic Elegance",
        "description": "우아하고 청순한 로맨틱 엘레강스 - 원피스 모델",
        "colors": ["#F5E6D3", "#D4AF37", "#FFF8E7"],
        "best_for": ["로맨틱", "우아한", "청순한", "드레스"],
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
            width: 96%;
            height: 96%;
            object-fit: contain;
            position: absolute;
            top: 2%;
            left: 2%;
            filter: brightness(1.08) saturate(1.05);
        }
        .overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to bottom,
                rgba(255, 248, 231, 0.3) 0%,
                rgba(245, 230, 211, 0.1) 50%,
                rgba(212, 175, 55, 0.25) 100%
            );
        }
        .soft-glow {
            position: absolute;
            width: 100%;
            height: 100%;
            background: radial-gradient(
                circle at 50% 20%,
                rgba(255, 248, 231, 0.4) 0%,
                transparent 50%
            );
            pointer-events: none;
        }
        .brand {
            position: absolute;
            top: 60px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 32px;
            font-weight: 300;
            color: #D4AF37;
            letter-spacing: 12px;
            text-transform: uppercase;
            text-shadow: 
                0 0 10px rgba(212, 175, 55, 0.5),
                0 0 20px rgba(212, 175, 55, 0.3),
                2px 2px 4px rgba(0,0,0,0.2);
            font-family: Georgia, serif;
        }
        .headline {
            position: absolute;
            bottom: 240px;
            left: 80px;
            right: 80px;
            text-align: center;
            font-family: Georgia, 'Playfair Display', serif;
            font-size: 68px;
            font-weight: 600;
            color: white;
            line-height: 1.3;
            letter-spacing: 0px;
            text-shadow: 
                0 0 30px rgba(212, 175, 55, 0.6),
                3px 3px 15px rgba(0,0,0,0.5);
        }
        .period {
            position: absolute;
            bottom: 180px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 26px;
            font-weight: 500;
            color: #D4AF37;
            letter-spacing: 4px;
            text-shadow: 
                0 0 10px rgba(212, 175, 55, 0.5),
                2px 2px 6px rgba(0,0,0,0.3);
            border-bottom: 2px solid rgba(212, 175, 55, 0.3);
            padding-bottom: 10px;
            margin: 0 200px;
        }
        .discount {
            position: absolute;
            bottom: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #FFF8E7 0%, #F5E6D3 100%);
            color: #D4AF37;
            padding: 35px 55px;
            border-radius: 50%;
            font-size: 68px;
            font-weight: 700;
            box-shadow: 
                0 0 0 3px #D4AF37,
                0 0 30px rgba(212, 175, 55, 0.4),
                0 10px 40px rgba(0,0,0,0.2);
            text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
        }
        .deco-line {
            position: absolute;
            bottom: 120px;
            left: 50%;
            transform: translateX(-50%);
            width: 300px;
            height: 1px;
            background: linear-gradient(
                to right,
                transparent,
                rgba(212, 175, 55, 0.5),
                transparent
            );
        }
    </style>
</head>
<body>
    <img src="{{IMAGE_URL}}" class="background-image" alt="Fashion Ad">
    <div class="overlay"></div>
    <div class="soft-glow"></div>
    <div class="brand">{{BRAND}}</div>
    <h1 class="headline">{{HEADLINE}}</h1>
    <div class="deco-line"></div>
    <div class="period">{{PERIOD}}</div>
    <div class="discount">{{DISCOUNT}}</div>
</body>
</html>"""
    }
}


def get_template(template_name: str) -> dict:
    """템플릿 가져오기"""
    return AD_TEMPLATES.get(template_name, AD_TEMPLATES["resort"])


def list_templates() -> list:
    """사용 가능한 템플릿 목록"""
    return ["resort", "retro", "romantic"]


# ⚠️ 임시 호환성 (제거 예정)
if "minimal" not in AD_TEMPLATES:
    AD_TEMPLATES["minimal"] = AD_TEMPLATES["resort"]
if "minima" not in AD_TEMPLATES:
    AD_TEMPLATES["minima"] = AD_TEMPLATES["resort"]
if "bold" not in AD_TEMPLATES:
    AD_TEMPLATES["bold"] = AD_TEMPLATES["retro"]
if "vintage" not in AD_TEMPLATES:
    AD_TEMPLATES["vintage"] = AD_TEMPLATES["romantic"]

print("✅ ad_templates loaded: resort, retro, romantic")