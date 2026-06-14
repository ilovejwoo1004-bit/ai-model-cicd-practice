# ---------------------------------------------------------
# FastAPI + 모델 파일을 포함한 MLOps 컨테이너 이미지
# ---------------------------------------------------------

FROM python:3.10

# 필요한 라이브러리 설치
RUN pip install matplotlib fastapi uvicorn scikit-learn joblib scipy

# 프로젝트 파일 복사
COPY app.py /app/app.py
COPY train_retrain.py /app/train_retrain.py
COPY train.py /app/train.py
COPY model.pkl /app/model.pkl
COPY reference.npy /app/reference.npy
COPY watch_reload.py /app/watch_reload.py

WORKDIR /app

# FastAPI 자동 reload 방식으로 실행 (watch_reload 사용)
CMD ["python3", "watch_reload.py"]

