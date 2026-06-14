import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

X = np.random.randn(200, 1)
y = (X[:, 0] > 0).astype(int)

model = RandomForestClassifier()
model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

np.save("reference.npy", X)

print("model.pkl, reference.npy 생성 완료")

