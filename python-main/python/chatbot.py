from flask import Flask, request, jsonify, current_app, abort
from sqlalchemy import create_engine, text
import requests, json
import urllib.request  # json api 가져오기
import sys
import pymysql
from konlpy.tag import Okt
from konlpy.tag import Kkma

# okt = Okt()
# kkma = Kkma()
application = Flask(__name__)


def get_info():
    # print('aaa')
    # 데이터베이스와 연결 설정
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='medicine',
        charset='utf8'
    )

    sql = "select idx, name, brand, price, image, info, category, link, rating_count from supplements"

    info_list = []
    with conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:  # pymysql.cursors.DictCursor : 결과를 딕셔너리로 가져온다는 것
            cur.execute(sql)
            result = cur.fetchall()
            info_list = []
            for data in result:
                info = {
                    'idx': data['idx'],
                    'name': data['name'],
                    'brand': data['brand'],
                    'price': data['price'],
                    'image': data['image'],
                    'info': data['info'],
                    'category': data['category'],
                    'link': data['link'],
                    'rating_count': data['rating_count']

                }
                info_list.append(info)

    return info_list


@application.route("/test", methods=['POST'])
def hello():
    info_list = get_info()
    usrMsg = request.get_json()
    usrMsg = usrMsg['userRequest']['utterance']
    keywordList = []

    for item in info_list:
        if "뼈" in usrMsg and "영양제" in usrMsg or "뼈에" in usrMsg or "뼈" in usrMsg:
            if "뼈" in item['info']:
                keyword = "뼈"
                keywordList.append(item)
        if "눈" in usrMsg and "영양제" in usrMsg or "눈에" in usrMsg or "눈" in usrMsg:
            if "눈" in item['info']:
                keyword = "눈"
                keywordList.append(item)
        if "소화" in usrMsg and "영양제" in usrMsg or "소화에" in usrMsg or "소화" in usrMsg:
            if "소화" in item['info']:
                keyword = "소화기계"
                keywordList.append(item)
        if "면역" in usrMsg and "영양제" in usrMsg or "면역에" in usrMsg or "면역" in usrMsg:
            if "면역" in item['info']:
                keyword = "면역기계"
                keywordList.append(item)
        if "항산화" in usrMsg and "영양제" in usrMsg or "항산화에" in usrMsg or "항산화" in usrMsg:
            if "항산화" in item['info']:
                keyword = "항산화제"
                keywordList.append(item)

    outputs = []

    service_msg = {
        'simpleText': {
            'text': "검색하신 " + keyword + "에 관련된 영양제리스트입니다."
        }
    }

    outputs.append(service_msg)
    for item in keywordList:
        # info = {
        #     'simpleText' : {
        #         'text':item['name']
        #     }
        # }
        # infoImg = {
        #     'simpleImage' : {
        #         'imageUrl' : item['image'],
        #         'altText' : 'aa'

        #     }
        # }
        info = {
            "basicCard": {
                "title": item['name'],
                # "description": item['info'],
                "thumbnail": {
                    "imageUrl": item['image']
                },
                "buttons": [
                    {
                        "action": "webLink",
                        "label": "구경하기",
                        # "webLinkUrl": "https://store.kakaofriends.com/kr/products/1542",
                        "webLinkUrl": item['link']
                    }
                ]
            }
        }

        outputs.append(info)
        # outputs.append(infoImg)

    res = {
        "version": "2.0",
        "template": {
            "outputs": outputs
        }
    }

    return jsonify(res)

    return "Hello goorm!"


@application.route("/test2", methods=['POST'])
def kakaoTest():
    print(request.get_json())
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    'simpleText': {
                        'text': 'Hello World'
                    }
                },
                {  # imageUrl이 https여야 하고, http면 안 되는 것 같음
                    "simpleImage": {
                        "imageUrl": 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/300px-Lion_waiting_in_Namibia.jpg',
                        "altText": "Hello"
                    }
                }
            ]
        }
    }
    return jsonify(res)


# 네이버톡톡
@application.route("/mychatbot", methods=['POST'])
def aaa():
    print(request.get_json())
    authKey = "Klv//KVeRtmBUsWVK/g/"
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Authorization': authKey
    }
    user_key = request.get_json()['user']
    msg = request.get_json()
    print(msg['textContent']['text'])

    info_list = get_info()  # db검색결과
    userMsg = msg['textContent']['text']  # 유저가 입력한 값

    keywordList = []
    keyword = ["뼈", "눈", "소화", "면역", "항산화"]

    for item in info_list:
        for key in keyword:
            if key in userMsg and "영양제" in userMsg or key + "에" in userMsg or key in userMsg:
                if key in item['info']:
                    keyword_user = key
                    keywordList.append(item)

    # 'rating_count' 값을 기준으로 내림차순 정렬
    sorted_keywordList = sorted(keywordList, key=lambda x: x['rating_count'], reverse=True)

    # 상위 3개 항목 추출
    top_3_keywords_list = sorted_keywordList[:3]

    data = {
        'event': 'send',
        'user': user_key,
        'textContent': {'text': f"검색하신 {keyword_user}에 관한 조회수 TOP3 영양제입니다."}
    }

    message = json.dumps(data)
    response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                             headers=headers,
                             data=message)

    for item in top_3_keywords_list:
        data = {  # 텍스트 응답
            'event': 'send',
            'user': user_key,
            'textContent': {'text': item['name']}
        }

        message = json.dumps(data)
        response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                                 headers=headers,
                                 data=message)
        data = {  # 링크 응답
            'event': 'send',
            'user': user_key,
            'textContent': {'text': item['link']},
        }

        message = json.dumps(data)
        response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                                 headers=headers,
                                 data=message)

        data = {  # 이미지 응답
            'event': 'send',
            'user': user_key,
            'imageContent': {'imageUrl': item['image']}
        }

        message = json.dumps(data)
        response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                                 headers=headers,
                                 data=message)

    print(response.text)  # 실제 응답 확인
    return 'a'


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
