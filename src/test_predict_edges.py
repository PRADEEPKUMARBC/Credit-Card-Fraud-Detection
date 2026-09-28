"""
Temporary edge-case test for Stage 8. Delete after verification.
"""

from predict import TransactionPredictor

predictor = TransactionPredictor()

# Build a valid baseline transaction (all zeros works for a quick test)
valid = {f"V{i}": 0.0 for i in range(1, 29)}
valid["Time"] = 0.0
valid["Amount"] = 0.0

print("\n--- Case 1: valid transaction (all zeros) ---")
print(predictor.predict(valid))

print("\n--- Case 2: MISSING a required feature (V5) ---")
broken = dict(valid)
broken.pop("V5")
try:
    predictor.predict(broken)
except ValueError as e:
    print("Caught ValueError as expected:")
    print(" ", str(e)[:120], "...")

print("\n--- Case 3: EXTRA key 'Class' sent by accident ---")
with_extra = dict(valid)
with_extra["Class"] = 1
result = predictor.predict(with_extra)
print("Result:", result)
print("(Notice: 'Class' was dropped, prediction proceeded normally.)")

print("\n--- Case 4: WRONG TYPE (not a dict) ---")
try:
    predictor.predict([1, 2, 3])
except TypeError as e:
    print("Caught TypeError as expected:")
    print(" ", str(e))