import requests

# 1. API URL
url = "https://domain.com/api/v1/crud/cars"  # 실제 API 주소로 변경

# 2. 요청 데이터
data = {
    "image_url": "https://your-bucket.s3.ap-northeast-2.amazonaws.com/images/car_123.jpg",
    "s3_key": "images/car_123.jpg",
    "car_number": "12가3456",
    "car_speed": 92,
    "x": 120,
    "y": 230,
    "w": 200,
    "h": 150,
}

# 3. 헤더 (예: 인증 토큰이 필요하다면 여기에 추가)
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer your_access_token"  # 필요 시 주석 해제
}


# 서버로 전송하는 함수
def send_to_server(data):
    global url
    global headers

    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response Body:", response.json())
