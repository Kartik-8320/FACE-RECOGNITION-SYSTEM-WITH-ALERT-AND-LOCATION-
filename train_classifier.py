import os
import numpy as np
import face_recognition
from collections import Counter
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import joblib

# Initialize the directories and lists
KNOWN_FACES_DIR = "D:/face-recognition-desktop/known_faces"
  # Set your correct path to the known faces directory
MODEL_PATH = "D:/face-recognition-desktop/model.pkl"
  # Set where to save the model

# Ensure the directories exist
if not os.path.exists(KNOWN_FACES_DIR):
    raise ValueError(f"Directory {KNOWN_FACES_DIR} does not exist!")

# Lists for storing encoded face vectors and labels
X = []  # Encoded face vectors
y = []  # Labels

# Debug: Print contents of the dataset
print("Loading images from:", KNOWN_FACES_DIR)

# Load face encodings and labels
for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if not os.path.isdir(person_dir):  # Skip non-directory files
        continue

    print(f"Processing {name}...")
    for file in os.listdir(person_dir):
        file_path = os.path.join(person_dir, file)
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                X.append(encodings[0])
                y.append(name)
            else:
                print(f"[INFO] No faces found in {file_path}")

# Check if any faces were loaded
if not X or not y:
    raise ValueError("No faces were found or loaded. Ensure your dataset contains valid images with faces.")

# Convert lists to numpy arrays
X = np.array(X)
y = np.array(y)

# Debug: Check how many faces have been loaded
print(f"Number of face encodings: {len(X)}")
print(f"Number of labels: {len(y)}")

# Count samples per class (person)
label_counts = Counter(y)
min_samples = min(label_counts.values())
print(f"Minimum samples per class: {min_samples}")

# Select the best k for k-NN
best_k = 1
best_score = 0
max_k = min(len(X), 10)  # Set an upper limit for k

if min_samples < 2:
    print("[WARNING] Not enough images per class for cross-validation. Using k=1 by default.")
    best_k = 1
else:
    for k in range(1, max_k + 1):  # Test for different k values up to min(10, len(X))
        knn = KNeighborsClassifier(n_neighbors=k)
        try:
            scores = cross_val_score(knn, X, y, cv=min(3, min_samples))  # Perform cross-validation
            score = scores.mean()
            print(f"k={k}, score={score:.4f}")
            if score > best_score:
                best_score = score
                best_k = k
        except ValueError as e:
            print(f"[WARNING] Skipping k={k}: {e}")

# Train the final model with the best k
print(f"[INFO] Training final model with k={best_k}...")
clf = KNeighborsClassifier(n_neighbors=best_k)
clf.fit(X, y)

# Save the trained model
joblib.dump(clf, MODEL_PATH)
print(f"[INFO] Model saved to {MODEL_PATH}")
