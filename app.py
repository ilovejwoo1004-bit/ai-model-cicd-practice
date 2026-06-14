"""
app.py
- FastAPI 실시간 예측 API
- 요청 데이터 누적 후 KS-test 기반 drift 감지
- drift 발생 시 incoming.npy 저장 및 자동 재학습 트리거
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import numpy as np
import joblib
from scipy.stats import ks_2samp
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys
import time

app = FastAPI()

# ---------------------------------------------------------
# 1. 모델과 기준(reference) 데이터 로드
# ---------------------------------------------------------
MODEL_PATH = "model.pkl"
REFERENCE_PATH = "reference.npy"
INCOMING_PATH = "incoming.npy"
DRIFT_PLOT_PATH = "drift_plot.png"
LOCK_FILE = "retrain.lock"

model = joblib.load(MODEL_PATH)
reference = np.load(REFERENCE_PATH).ravel()   # 1차원 기준 분포
incoming_samples = []                         # shape: [ [f1, f2, f3], ... ]
model_loaded_at = time.strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------
# 2. Drift 시각화 함수
# ---------------------------------------------------------
def save_drift_plot(reference_1d, incoming_1d, p_value):
    """
    reference vs incoming 분포 비교 그래프 저장
    """
    plt.figure(figsize=(10, 6))

    plt.hist(reference_1d, bins=30, alpha=0.6, label="Reference", density=True)
    plt.hist(incoming_1d, bins=30, alpha=0.6, label="Incoming", density=True)

    plt.title(f"Data Drift Detection (p-value={p_value:.6f})")
    plt.xlabel("Score")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(DRIFT_PLOT_PATH)
    plt.close()

# ---------------------------------------------------------
# 3. 기본 확인용 API
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"message": "MLOps FastAPI server is running"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "pid": os.getpid(),
        "model_loaded_at": model_loaded_at,
        "buffer_size": len(incoming_samples),
        "model_exists": os.path.exists(MODEL_PATH),
        "reference_exists": os.path.exists(REFERENCE_PATH),
    }

@app.get("/drift-image")
def drift_image():
    if os.path.exists(DRIFT_PLOT_PATH):
        return FileResponse(DRIFT_PLOT_PATH, media_type="image/png")
    return JSONResponse(
        status_code=404,
        content={"message": "drift_plot.png not found"}
    )

# ---------------------------------------------------------
# 4. 예측 API
# ---------------------------------------------------------
@app.get("/predict")
def predict(f1: float, f2: float, f3: float):
    """
    입력된 3개 feature 값에 대해 예측을 수행하고,
    incoming 데이터를 누적하여 drift 여부를 반환한다.
    """

    sample = [f1, f2, f3]
    incoming_samples.append(sample)

    drift_detected = False
    p_value = None

    # ---------------------------------------------------------
    # Drift 감지: 50개 이상 쌓이면 KS-test 수행
    # ---------------------------------------------------------
    if len(incoming_samples) >= 50:
        incoming_array = np.array(incoming_samples)        # (N, 3)
        incoming_score = incoming_array.mean(axis=1)       # 1D score

        stat, p_value = ks_2samp(reference, incoming_score)
        drift_detected = bool(p_value < 0.05)

        if drift_detected and not os.path.exists(LOCK_FILE):
            print(" Drift 감지 → incoming.npy 저장 및 재학습 실행")

            # lock 생성
            open(LOCK_FILE, "w").close()

            # incoming 전체 feature 저장
            np.save("incoming_tmp.npy", incoming_array)
            os.replace("incoming_tmp.npy", INCOMING_PATH)

            # drift plot 저장
            save_drift_plot(reference, incoming_score, p_value)

            # 자동 재학습 실행
            subprocess.Popen([sys.executable, "train_retrain.py"])

    # -------------------------------------------------------
    # 모델 예측 수행
    # -------------------------------------------------------
    pred = model.predict([sample])

    return {
        "input": {"f1": f1, "f2": f2, "f3": f3},
        "prediction": int(pred[0]),
        "drift_detected": drift_detected,
        "p_value": None if p_value is None else float(p_value),
        "sample_size": len(incoming_samples)
    }

