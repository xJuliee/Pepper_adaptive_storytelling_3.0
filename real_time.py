import cv2
import numpy as np
from keras.models import load_model

# Load the trained CNN model
model = load_model("CNNs/Final_CNN.keras")

# Reverse mapping from class index to label
class_mapping = {
    0: "angry",
    1: "confused",
    2: "disgust",
    3: "fear",
    4: "happy",
    5: "neutral",
    6: "sad",
    7: "surprise"
}

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Input image size expected by the model
IMG_SIZE = (75, 75)

def preprocess_face(gray_face):
    """Resize, equalize histogram, normalize, and reshape a face image for model prediction."""
    face_resized = cv2.resize(gray_face, IMG_SIZE)
    face_equalized = cv2.equalizeHist(face_resized)
    face_normalized = face_equalized / 255.0
    face_normalized = np.expand_dims(face_normalized, axis=-1)  # Shape: (75, 75, 1)
    face_input = np.expand_dims(face_normalized, axis=0)        # Shape: (1, 75, 75, 1)
    return face_input

# Start the webcam
cap = cv2.VideoCapture(0)
print("Press 'q' to exit...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using Haar cascade
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_gray = gray[y:y+h, x:x+w]
        face_input = preprocess_face(face_gray)

        # Predict emotion probabilities
        predictions = model.predict(face_input, verbose=0)
        class_id = np.argmax(predictions)
        emotion_label = class_mapping[class_id]

        # Print probabilities to console
        print("\nEmotion probabilities:")
        for idx, prob in enumerate(predictions[0]):
            print(f"{class_mapping[idx]}: {prob * 100:.2f}%")

        # Draw bounding box around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Show top prediction above the bounding box
        cv2.putText(frame, f"{emotion_label} ({predictions[0][class_id]*100:.1f}%)",
                    (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        # Show top 3 predictions below the bounding box
        top_indices = np.argsort(predictions[0])[::-1][:3]
        for i, idx in enumerate(top_indices):
            label = f"{class_mapping[idx]}: {predictions[0][idx]*100:.1f}%"
            cv2.putText(frame, label, (x, y + h + 20 + i*25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

    # Display the processed video frame
    cv2.imshow("Real-Time Emotion Detection", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close windows
cap.release()
cv2.destroyAllWindows()