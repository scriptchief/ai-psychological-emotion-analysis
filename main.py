import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from collections import defaultdict, Counter

# Yüz tanıma için OpenCV'nin hazır modelini yükle
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Duygu tanıma modelini yükle
emotion_model = load_model('FER_model.h5')

# Videoyu yükle
cap = cv2.VideoCapture('25snemotion.mp4')

# Teşhis süresini ayarla (örneğin, her 10 saniyede bir)
diagnosis_interval = 10  # saniye
fps = cap.get(cv2.CAP_PROP_FPS)  # Saniye başına düşen frame sayısı
frames_per_interval = int(fps * diagnosis_interval)

# Duyguların kaydedildiği yapı
emotions_dict = defaultdict(list)

current_frame = 0
while True:
    # Video'dan bir frame al
    ret, frame = cap.read()
    if not ret:
        break

    # Griye çevir
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Yüzleri tespit et
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Yüz bölgesini kes
        roi_gray = gray[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        roi = roi_gray.astype('float')/255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        # Duygu tahmini yap
        predictions = emotion_model.predict(roi)[0]
        emotion_label = np.argmax(predictions)

        # Duygu etiketini ekrana yaz
        label_map = ['Kızgın', 'Tiksindirici', 'Korkmuş', 'Mutlu', 'Üzgün', 'Şaşırmış', 'Nötr']
        predicted_emotion = label_map[emotion_label]
        cv2.putText(frame, predicted_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        # Duygu kaydı
        interval = current_frame // frames_per_interval
        emotions_dict[interval].append(predicted_emotion)

    # Videonun işlenmiş halini göster
    cv2.imshow('Emotion Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    current_frame += 1

# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()

# Duygu analizi sonuçlarını analiz et ve sun
for interval, emotions in emotions_dict.items():
    emotion_count = Counter(emotions)
    print(f"Zaman Aralığı {interval * diagnosis_interval} - {(interval + 1) * diagnosis_interval} saniye:")
    print(emotion_count)
    print("\n")
