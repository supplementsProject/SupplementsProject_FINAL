from flask import Flask,request, jsonify, current_app, abort
from sqlalchemy import create_engine, text
import requests, json
import urllib.request #json api 가져오기
import sys
import pymysql

application = Flask(__name__)

def get_info():
    #print('aaa')
    #데이터베이스와 연결 설정
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
        with conn.cursor(pymysql.cursors.DictCursor) as cur: # pymysql.cursors.DictCursor : 결과를 딕셔너리로 가져온다는 것
            cur.execute(sql)
            result = cur.fetchall()
            info_list = []
            for data in result:
                info = {
                    'idx' : data['idx'],
                    'name' : data['name'],
                    'brand' : data['brand'],
                    'price' : data['price'],
                    'image' : data['image'],
                    'info' : data['info'],
                    'category' : data['category'],
                    'link' : data['link'],
                    'rating_count' : data['rating_count']
                    
                }
                info_list.append(info)
                
    return info_list

#네이버톡톡
@application.route("/mychatbot", methods=['POST'])
def aaa():
    print(request.get_json())
    authKey = "Klv//KVeRtmBUsWVK/g/"
    headers = {
        'Content-Type':'application/json;charset=UTF-8',
        'Authorization':authKey
    }
    user_key = request.get_json()['user']
    msg = request.get_json()
    print(msg['textContent']['text'])
    
    info_list = get_info() # db검색결과
    userMsg = msg['textContent']['text']   # 유저가 입력한 값
    
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
                'event' : 'send',
                'user' : user_key,
                'textContent' : {'text': f"검색하신 {keyword_user}에 관한 조회수 TOP3 영양제입니다."}
        }
    
    message = json.dumps(data)
    response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                                headers=headers,
                                data=message)
    
    for item in top_3_keywords_list:
        data = { # 링크 응답
            'event' : 'send',
            'user' : user_key, 
            'compositeContent' : {
                'compositeList' : [
                    {
                        'image' : {'imageUrl' : item['image']},
                        'buttonList': [
                            {
                                'type' : 'LINK',
                                'data' : {
                                    'title' : '상세 페이지로 이동하기',
                                    'url' : 'http://localhost:8080/detail'
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        message = json.dumps(data)
        response = requests.post('https://gw.talk.naver.com/chatbot/v1/event',
                                    headers=headers,
                                    data=message)
        
    print(response.text)  # 실제 응답 확인
    return 'a'


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
