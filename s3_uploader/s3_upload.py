import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# .env 로드
load_dotenv()

# 환경변수 가져오기
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
REGION = os.getenv("AWS_S3_REGION")
# .env 로드
load_dotenv()

# 환경변수 가져오기
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
REGION = os.getenv("AWS_S3_REGION")

# S3 클라이언트 생성
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def upload_image_to_cars_folder(image_path):
    if not os.path.isfile(image_path):
        print("❌ 파일이 존재하지 않습니다.")
        return None

    original_filename = os.path.basename(image_path)
    s3_key = f"cars/{original_filename}"

    try:
        s3.upload_file(image_path, BUCKET_NAME, s3_key)

        s3_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{quote_plus(s3_key)}"

        print("✅ 업로드 성공:")
        print(f"• original_filename: {original_filename}")
        print(f"• s3_key: {s3_key}")
        print(f"• s3_url: {s3_url}")

        return {
            "original_filename": original_filename,
            "s3_key": s3_key,
            "s3_url": s3_url
        }

    except NoCredentialsError:
        print("❌ AWS 자격증명이 유효하지 않습니다.")
        return None


metadata = upload_image_to_cars_folder("supervised_learning_visual.jpg")
if metadata:
    print("\n메타데이터 저장용 객체:")
    print(metadata)