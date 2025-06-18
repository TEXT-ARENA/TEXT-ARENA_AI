import json
import boto3
import base64
import uuid
from backend import generate_character_stat, generate_weapon_stat, generate_shoes_stat, generate_hat_stat, generate_top_stat, generate_image_from_prompt

s3_client = boto3.client('s3')
BUCKET_NAME = 'inha-pj-03-s3-img'

def lambda_handler(event, context):
    path = event.get("path", "")
    http_method = event.get("httpMethod", "")
    body = event.get("body")
    if body:
        body = json.loads(body)
    
    # 캐릭터 생성 API
    if path == "/api/characters" and http_method == "POST":
        name = body.get("characterName")
        desc = body.get("description")
        result = generate_character_stat(name, desc)
        try:
            data = json.loads(result)
            return {
                "statusCode": 200,
                "body": json.dumps({"isSuccess": True, "result": data})
            }
        except json.JSONDecodeError:
            return {
                "statusCode": 200,
                "body": json.dumps({"isSuccess": True, "raw_result": result})
            }
    # 장비 생성 API
    elif path == "/api/equipments" and http_method == "POST":
        # 1. 요청 본문에서 'part', 'description', 'equipmentType'을 추출
        try:
            part = body.get("equipmentType")
            equipmentName = body.get("equipmentName")
            description = body.get("description")

            if not part or not description:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"isSuccess": False, "message": "part와 description은 필수입니다."})
                }
            
            # 2. 'part'에 따라 적절한 장비 생성 함수 호출
            result = None

            # 이미지 생성 및 S3 업로드 
            image_bytes = generate_image_from_prompt(part, equipmentName, description)
            if not image_bytes:
                # 이미지 생성 실패 시
                return {
                    "statusCode": 503,
                    "body": json.dumps({
                        "isSuccess": False,
                        "message": "이미지 생성에 실패했습니다. 프롬프트/입력값/모델 상태를 확인하세요."
                    })
                }
            
            file_url = None
            try:
                file_name = str(uuid.uuid4()) + ".jpg"

                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=file_name,
                    Body=image_bytes,      
                    ContentType='image/jpeg'
                )

                file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
                
            except Exception as e:
                print(f"AWS 이미지 생성 중 오류 발생: {e}")
 

            if part == "weapon":
                result = generate_weapon_stat(equipmentName, description)
            elif part == "top":
                result = generate_top_stat(equipmentName, description)
            elif part == "hat":
                result = generate_hat_stat(equipmentName, description)
            elif part == "shoes":
                result = generate_shoes_stat(equipmentName, description)
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"isSuccess": False, "message": f"'{part}'는 유효한 장비 부위가 아닙니다."})
                }

            # 3. 생성된 결과를 성공 응답으로 포장하여 반환
            try:
                data = json.loads(result)
                data["imageUrl"] = file_url
                return {
                    "statusCode": 200,
                    "body": json.dumps({"isSuccess": True, "result": data})
                }
            except json.JSONDecodeError:
                # Bedrock이 JSON이 아닌 일반 텍스트를 반환한 경우를 대비
                return {
                    "statusCode": 200,
                    "body": json.dumps({"isSuccess": True, "raw_result": result})
                }

        except Exception as e:
            print(f"[ERROR] An unhandled exception occurred in the Lambda function: {e}")
            
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "isSuccess": False,
                    "message": "서버 내부에서 장비 생성 중 오류가 발생했습니다.",
                })
            }


