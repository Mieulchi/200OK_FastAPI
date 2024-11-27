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

client = OpenAI(api_key = api_key )
class MonoRequest(BaseModel):
    content: Optional[str] = "" #이미지 묘사 텍스트
class StoryRequest(BaseModel):
    choice: Optional[str] = None  # 선택적 필드로 설정
    beforeContent: Optional[str] = ""  # 이전 생성된 내용을 저장하는 선택적 필드, 기본값은 빈 문자열
class ImageRequest(BaseModel):
    description: Optional[str] = None #이미지 묘사 텍스트



#로딩 독백 대사
@app.post("/generate_monologue")
async def generate_monologue(request: MonoRequest):

    content = request.content

    content_message = f"플레이어가 처한 상황은 {content}이야."

    try:
        # OpenAI API 호출하여 스토리 생성
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type":"json_object"},     
          messages=[
    {
        "role": "system",
        "content": (
            "스토리기반 어드벤처 게임에서 현재 상황을 기반으로 플레이어가 하는 생각과 독백들을 만드는 AI야. .json"
            "이 게임에서 플레이어는 우주비행을 하다 아마존으로 불시착하여 아마존 정글에 고립되어 생존을 해야하는 상황이야 "
            "주어진 상황과 플레이어가 선택한 선택지를 기반으로 플레이어가 할법한 생각과 독백대사들을 한 문장씩 10개 생성해줘."
            "플레이어는 두려움에 차있는 상태야"
            "말투는 부드럽고 감정적인 말투로 해줘"
            "말은 항상 한글로 해."
            "맞춤법을 틀리지 않게 해줘"
            "사람이 말하는 것처럼 자연스러운 문장을 생성해줘"
            "AI느낌이 나지 않게 문장을 생성해줘"
            "실제 해당 상황에 처한 사람이 할법한 말을 해줘"
            "자연스러운 어휘를 사용해줘"
            "반환 형식은 JSON 형식으로 한 문장씩 10개의 대사를 리스트에 담아 반환해야 하고, 어울리는 배경음악 태그를 반환해야해 필드는 다음과 같아:"
            "-`monologue`: 플레이어가 현재 상황에서 할만한 말"
            "-`tag`: monologue에 공통적으로 어울리는 배경음악 태그"
            "`tag`는 [ Peaceful, Tense,  Dangerous, Scary,  Jungle Sounds, Animal Sounds, River Sounds, Battle, Sad, Lonely ] 이 중 하나를 선택한다."
            "`monologue`는 한 문장씩 10개의 문장을 생성한다. 리스트에는 10개의 대사가 들어가 있다."
            
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
        raise HTTPException(status_code=500, detail=f"Error generating monologue: {e}")




 #이미지 생성
@app.post("/generate_image")
async def generate_story(request: ImageRequest):
    desc = request.description

    try:
        response = client.images.generate(
             model="dall-e-3",
             prompt=desc,
             size="1024x1024",
             quality="hd",
             n=1,
            )
        # 이미지 URL 추출
        image_url = response.data[0].url

         # JSON 형태로 변환
        return {"image_url": image_url}
    
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")


# 스토리 생성
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
            "'선택지에 없는 행동을 하면 다시 올바르게 선택하라고 알려줘."
            "'물을 먹는다.', '음식을 먹는다.' 같은 음식과 물을 소비하는 경우는 없어. 물과 음식은 플레이어가 직접 선택하여 먹을 수 있게 따로 관리하고 있어."
            "반환 형식은 JSON 형식으로 해야 하고, 각 필드는 다음과 같아:"
            "content,choice1,choice2,choice3 필드의 말투는 '~다' 체를 써"
            "사용자의 질문이 '게임을 시작해줘'일 경우에 water,food의 변화량은 무조건 0이야"
            "- `content`: 현재 상황 설명"
            "- `choice1`, `choice2`, `choice3`: 플레이어가 선택할 수 있는 세 가지 선택지 텍스트"
            "- `water`: 현재 선택이 물에 미치는 변화량 (변화량 범위는: -1, 0, 1, 2, 3)"
            "- `food`: 현재 선택이 음식에 미치는 변화량 (변화량 범위는 : -1, 0, 1, 2, 3)"
            "- `damage`: 현재 선택이 플레이어에게 입히는 피해(피해량 범위는 : 0 ~ 5)"
            "- `description`: 텍스트만보고 그림을 그릴 수 있게 현재 상황의 한 순간을 글로 표현,주어(주어는 무조건 남자로 한다.) 목적어 서술어가 무조건 있어야 한다. (예: 우주복을 입고 아마존의 풀숲에서 앉아서 휴식을 취하고 있는 한 남자. 뒤에는 남자가 탔던 우주선이 있다.) 예시를 똑같이 쓰지마"
            "- `causeOfDeath`: 만약 현재 상황에서 사망한다면 어떤 사유로 사망하게 되는지 20글자 내외로 설명. 문장의 끝은 '사망...'로 끝나야하고 매끄럽게 연결이 되어야해. 현재 상황과 연관이 있고 논리적으로 납득이 되는 사망사유여야한다. 사망 상황이 아니더라도, 현재 상황과 관련된 사망 원인을 반드시 포함해야한다. 사망사유는 잔인하지 않아야해.ex) 나무 밑에 있는 독버섯을 먹고 사망..."
            "상황에 맞게 water,food,damage 변화량을 잘 설정해줘."
            "모든 필드는 빈 값("")을 가질 수 없어."
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
        raise HTTPException(status_code=500, detail=f"Error generating story: {e}")

# FastAPI 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
