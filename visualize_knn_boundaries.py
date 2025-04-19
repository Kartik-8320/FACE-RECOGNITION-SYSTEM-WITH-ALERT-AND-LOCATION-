import os
import numpy as np
import face_recognition
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import LabelEncoder

KNOWN_FACES_DIR = "known_faces"

print("[INFO] Loading and encoding known faces...")

X = []
y = []

for person_name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
    if not os.path.isdir(person_dir):
        continue

    for image_name in os.listdir(person_dir):
        image_path = os.path.join(person_dir, image_name)
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            X.append(encodings[0])
            y.append(person_name)

X = np.array(X)
y = np.array(y)

print("[INFO] Reducing dimensionality with PCA...")
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)

k = min(3, len(X_reduced))
clf = KNeighborsClassifier(n_neighbors=k)
clf.fit(X_reduced, y)

print("[INFO] Plotting decision boundaries...")

# Define colormap before plotting
cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF', '#FFD700', '#FFA07A'])
cmap_bold = ['red', 'green', 'blue', 'gold', 'darkorange']

h = .05  # step size in the mesh
x_min, x_max = X_reduced[:, 0].min() - 1, X_reduced[:, 0].max() + 1
y_min, y_max = X_reduced[:, 1].min() - 1, X_reduced[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

# Convert labels to numbers for plotting
le = LabelEncoder()
y_encoded = le.fit_transform(y)
clf.fit(X_reduced, y_encoded)

Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

# Plot the decision boundaries
plt.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.6)

# Plot the data points
for i, label in enumerate(le.classes_):
    idx = np.where(y_encoded == i)
    plt.scatter(X_reduced[idx, 0], X_reduced[idx, 1], c=cmap_bold[i % len(cmap_bold)], label=label, edgecolor='k')

plt.legend()
plt.title("KNN Decision Boundaries (PCA-Reduced Face Encodings)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.grid(True)
plt.show()
