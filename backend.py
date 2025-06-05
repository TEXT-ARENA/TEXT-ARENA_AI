"""
backend.py
2025.06.04, Seungjun Lee
"""
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_character_stat(name, char_desc):
    prompt = """
    너는 RPG 게임 캐릭터 생성기야.
    
    사용자가 자유롭게 캐릭터를 설명하면,
    아래의 stat(key-value) 값만 사용자의 설명에 맞게 최대한 합리적으로 숫자를 추정해서 JSON 객체로 만들어.
    그리고, 사용자가 입력한 캐릭터 설명에서 특별히 강조되거나, 캐릭터의 인상/특징과 밀접하게 연결된 속성(예: '힘이 엄청 세다', '엄청 빠르다', '거대한 곰처럼 우직하다' 등)에만,
    그 stat에 대해 'hp_reason'처럼 인상, 감탄, 이미지, 짧은 느낌 위주로 reason을 추가해.
    그 외 별다른 특징이 없는 속성은 reason 없이 값만 출력해도 좋아.
    절대로 수치적 근거나 분석적인 문장 쓰지 말고, 느낌·감성 위주로 적어.
    
    반드시 포함할 key:
    - hp (체력)
    - attack (공격력)
    - defense (방어력)
    - criticalChance (치명타 확률, 0~1 소수, 예: 0.10)
    - criticalDamage (치명타 피해 배수, 예: 1.5)
    - speed (속도, 0~100)
    - dodgeChance (회피율, 0~1 소수, 예: 0.05)
    - accuracy (명중률, 0~1 소수, 예: 0.92)
    
    출력 예시:
    {
      "hp": 120,
      "hp_reason": "거대한 곰 같은 덩치라서, 체력은 무조건 높아야지!",
      "attack": 10,
      "defense": 8,
      "criticalChance": 0.08,
      "criticalDamage": 1.4,
      "speed": 30,
      "speed_reason": "이런 친구는 빠르진 않을 듯. 묵직~",
      "dodgeChance": 0.04,
      "accuracy": 0.88
    }
    
    중요:
    - 반드시 JSON 코드만 출력해. (설명, 해설, 안내 등 X)
    - 숫자는 항상 예시처럼 소수점 자릿수까지 표기해.
    - 사용자가 강조한 속성에만 느낌 위주의 reason을 추가하고, 나머지는 값만 출력.
    """

    
    user_prompt = f"캐릭터 설명: {char_desc}"
    
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 600,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt + user_prompt}],
                }
            ],
        }
    )
    # Bedrock 호출
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=body,
    )
    response_body = json.loads(response.get("body").read())
    output_text = response_body["content"][0]["text"]
    return output_text

def generate_weapon_stat(weapon_desc):
    prompt = """
    너는 RPG 무기 정보 생성기야.
    
    아래 무기 설명을 읽고, 설명에 어울리는 무기의 이름은 반드시 한국어로 정하고, bonusType, effects를 스스로 판단해서 예시와 같은 JSON 포맷으로만 출력해.
    무기의 bonusType에는 아래 8가지만 존재한다는 점을 참고해줘:
    - hpBonus
    - attackBonus
    - defenseBonus
    - criticalChanceBonus
    - criticalDamageBonus
    - speedBonus
    - dodgeChanceBonus
    - accuracyBonus
    
    그리고, 사용자가 입력한 무기 설명에서 특별히 강조되거나, 캐릭터성/무기 특성과 밀접하게 연결된 속성(예: '불타는', '매우 빠른', '치명적인' 등)에는 그 속성에 대해서만 인상, 감탄, 이미지, 짧은 느낌 위주로 reason을 'stat이름_reason' 형태로 추가해.
    그 외에 별다른 특성이 없는 속성은 reason 없이 값만 출력해도 좋아.
    
    예시:
    {
      "weapon": {
        "name": "맹독 단검",
        "name_reason": "이거 한 번 맞으면 몸에 독이 쫙 퍼질 것 같네?",
        "bonusType": "attackBonus",
        "bonusValue": 3,
        "effects": [
          {
            "type": "poison",
            "type_reason": "독이라니, 진짜 상대방 고생 좀 하겠는데?",
            "chance": 0.25,
            "duration": 3,
            "damageForTurn": 5
          }
        ]
      }
    }
    
    주의사항:
    - 반드시 JSON 코드만 출력해. (설명, 해설, 안내문 없이)
    - 무기 이름(name)은 반드시 한국어로 출력할 것.
    - key 이름, 구조, 소수점 표기, 배열 등은 반드시 예시와 동일하게 맞출 것.
    - bonusType에는 반드시 위 8개 중 하나만 사용.
    - 사용자의 무기 설명에서 특성이 강조된 속성에만 reason을 붙이고, 그 외에는 reason 없이 값만 출력할 것.
    - effects 배열이 비어있을 수도 있음.
    """

    user_prompt = f" 무기 설명: {weapon_desc}"
    
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 600,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt + user_prompt}],
                }
            ],
        }
    )
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=body,
    )
    response_body = json.loads(response.get("body").read())
    output_text = response_body["content"][0]["text"]
    return output_text
