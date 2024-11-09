import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional  # Optional을 사용하기 위해 추가
import json  

app = FastAPI()

# .env 파일에서 환경 변수 로드
load_dotenv()
# 환경 변수 가져오기
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
class StoryRequest(BaseModel):
    choice: Optional[str] = None  # 선택적 필드로 설정
    beforeContent: Optional[str] = ""  # 이전 생성된 내용을 저장하는 선택적 필드, 기본값은 빈 문자열

@app.post("/generate_story")
async def generate_story(request: StoryRequest):
    # choice 값이 없으면 기본값으로 "게임을 시작해줘" 사용
    choice_value = request.choice or "게임을 시작해줘"
    before_content = request.beforeContent
    if before_content == "":
        content_message = f"{choice_value}를 선택"
    else:
        content_message = f"직전 상황과 선택지는 {before_content}고, {choice_value}를 선택"

    try:
        # OpenAI API 호출하여 스토리 생성
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type":"json_object"},     
          messages=[
    {
        "role": "system",
        "content": (
            "너는 선택 기반의 몰입형 어드벤처 게임 스토리를 전문적으로 만드는 AI야. .json"
            "이 게임에서 플레이어는 우주비행을 하다 아마존으로 불시착하여 아마존 정글에 고립되어 생존하고 탈출하기 위해 결정을 내려야 해. "
            "각 상황에 대해 서술형 설명을 제공하고, 세 가지 선택지를 줘. "
            "각 선택지는 새로운 상황으로 이어지고, 또 다른 이야기와 세 가지 선택지를 제공해."
            "모든 상황은 이전의 상황과 연결이 되어야해. 대신 처음 게임을 시작하는경우는 예외야"
            "플레이어가 이 모험을 통해 생존하고 정글에서 탈출할 수 있도록 안내해줘. "
            "말은 항상 한글로 해."
            "현재 상황을 설명할때는 최대한 자세하게 설명해줘 3줄이상"
            "맹수를 만나기, 절벽을 마주치기, 넘어져서 상처를 입기, 기상악화 등등 여러 극적인 상황들도 생성해줘"
            "선택지에 없는 행동을 하면 다시 올바르게 선택하라고 알려줘."
            "반환 형식은 JSON 형식으로 해야 하고, 각 필드는 다음과 같아:"
            "사용자의 질문이 '게임을 시작해줘'일 경우에 water,food의 변화량은 무조건 0이야"
            "- `content`: 현재 상황 설명"
            "- `choice1`, `choice2`, `choice3`: 플레이어가 선택할 수 있는 세 가지 선택지 텍스트"
            "- `water`: 각 선택이 물에 미치는 변화량 (예: -3,-2,-1, 1, 2, 3)"
            "- `food`: 각 선택이 음식에 미치는 변화량 (예: -3,-2,-1, 1, 2, 3)"
            "- `description`: 텍스트만보고 그림을 그릴 수 있게 현재 상황의 한 순간을 글로 표현,주어(주어는 무조건 남자로 한다.) 목적어 서술어가 무조건 있어야 한다. (예: 우주복을 입고 아마존의 풀숲에서 앉아서 휴식을 취하고 있는 한 남자. 뒤에는 남자가 탔던 우주선이 있다.) 예시를 똑같이 쓰지마"
        )
    },
    {
        "role": "user",
        "content": content_message 
    }
]


        )

     # 응답 내용에 접근할 때 속성 접근 방식 사용
        message_content = response.choices[0].message.content

        # JSON으로 파싱
        parsed_content = json.loads(message_content)  

        return parsed_content

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Error generating story: {e}")

# FastAPI 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
