"""
train.py
- 최초의 학습 데이터로 3개 feature 모델을 학습하고 model.pkl로 저장
- 학습 데이터 분포(reference.npy)를 저장하여 drift 감지 기준으로 사용
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

np.random.seed(42)

# ---------------------------------------------------------
# 1. 학습 데이터 생성 (3개 feature)
# ---------------------------------------------------------
n_samples = 500

X = np.random.randn(n_samples, 3)

# rule 기반 이진 라벨 생성
# f1, f2, f3의 조합으로 클래스 결정
score = X[:, 0] + 0.8 * X[:, 1] - 0.5 * X[:, 2]
y = (score > 0).astype(int)

# ---------------------------------------------------------
# 2. 모델 학습
# ---------------------------------------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X, y)

# ---------------------------------------------------------
# 3. drift 기준 데이터 저장
# ---------------------------------------------------------
# KS-test는 1차원 비교가 필요하므로 3개 feature를 mean score로 축소
reference_score = X.mean(axis=1)

joblib.dump(model, "model.pkl")
np.save("reference.npy", reference_score)

print(" 초기 학습 완료")
print(" - model.pkl 생성")
print(" - reference.npy 생성")
print(f" - X shape: {X.shape}")
print(f" - y class counts: {np.bincount(y)}")

