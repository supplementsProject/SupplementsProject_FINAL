import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="1234",
    database="medicine"
)

# supplements = ("""
# CREATE TABLE  supplements(idx INT AUTO_INCREMENT PRIMARY KEY
# ,name longtext NOT NULL
# ,brand VARCHAR(100) NOT NULL
# ,price VARCHAR(50) NOT NULL
# ,image VARCHAR(100) NOT NULL
# ,nutrient_info longtext NOT NULL
# ,info longtext NOT NULL
# ,use_info longtext NOT NULL
# ,caution longtext NOT NULL
# ,category VARCHAR(20)
# ,rating_count int NOT NULL)
# """)
cursor = mydb.cursor() # sql문을 실행할 수 있는 작업환경을 제공하는 객체
# cursor.execute(supplements)

# res_list = ["https://kr.iherb.com/c/bone-joint-cartilage",
#         "https://kr.iherb.com/c/immune-support",
#         "https://kr.iherb.com/c/antioxidants",
#         "https://kr.iherb.com/c/digestive-support"]
res = requests.get('https://kr.iherb.com/c/digestive-support')
soup = BeautifulSoup(res.content, 'html.parser')
url_list = []

# 웹 페이지에서 'div' 태그 중 클래스가 'best-sellers-image'인 요소를 찾아서 리스트에 추가
div = soup.find('div', class_='absolute-link-wrapper')
div.extract()
div_tag = soup.find_all('div', class_='absolute-link-wrapper')
for div in div_tag[:10]:
    a_tag = div.find('a')
    if a_tag:
        url = a_tag.get('href') # a태그의 href 속성을 가져옴
        url_list.append(url) # url을 url_list에 추가한다

# 빈 리스트를 생성하여 추출한 데이터를 저장할 준비
data_list = []

for url in url_list:
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    div_tag = soup.find('div', class_='supplement-facts-container').find_all('tr')[0] # 영양성분정보 없애기 위함
    div_tag.extract()

    title_name = soup.find('h1', id='name') # 상품 이름
    title_brand = soup.find('span', itemprop='name') # 상품 제조사
    title_price = soup.find('div', class_='price-inner-text') # 상품 가격
    title_image = soup.find('img', id='iherb-product-image') # 상품 이미지
    title_table = soup.find('div', class_='supplement-facts-container') # 영양 성분 정보
    title_info = soup.find('div', itemprop='description') # 상품 설명
    title_use = soup.find_all('div', class_='prodOverviewDetail')[0] # 상품 사용법
    title_caution = soup.find_all('div', class_='prodOverviewDetail')[1] # 상품 주의사항
    title_rating = soup.find('div', class_='rating').find('span') # 리뷰 수

    if title_table:
        # 테이블 안의 모든 <tr> 요소 찾기
        tr_elements = title_table.find_all('tr')

        # 각 <tr> 요소에서 텍스트 추출하고 개행 문자로 연결
        merged_text = '\n'.join([tr.get_text(strip=True, separator='\t') for tr in tr_elements])
    else:
        print("title_table를 찾을 수 없습니다.")

    # 추출한 데이터를 딕셔너리로 저장
    product_data = {
        "name": title_name.get_text().strip() if title_name else "N/A",
        "brand": title_brand.get_text() if title_brand else "N/A",
        "price": title_price.get_text().strip() if title_price else "N/A",
        "image": title_image.get('src') if title_image else "N/A",
        "nutrient info": merged_text if merged_text else "N/A",
        "info": title_info.get_text().strip() if title_info else "N/A",
        "use": title_use.get_text().strip() if title_use else "N/A",
        "caution": title_caution.get_text().strip() if title_caution else "N/A",
        "rating": int(title_rating.get_text().strip().replace(",", "")) if title_rating else "N/A"
    }

    # 데이터를 리스트에 추가
    data_list.append(product_data)

# 리스트를 데이터 프레임으로 변환
df = pd.DataFrame(data_list)

# 데이터 프레임을 테이블 형태로 출력
print(df)

insert_query = """
    INSERT INTO supplements ( name, brand, price, image, nutrient_info, info, use_info, caution, rating_count ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for index, row in df.iterrows():
    data = (
        row['name'],
        row['brand'],
        row['price'],
        row['image'],
        row['nutrient info'],
        row['info'],
        row['use'],
        row['caution'],
        row['rating']
    )
    cursor.execute(insert_query, data)
    mydb.commit()

cursor.close()
mydb.close()