import face_recognition as fr
import cv2
import numpy as np
import cv2
import face_recognition as fr
from PIL import Image
import easyocr
reader = easyocr.Reader(['ch_sim','en'])
def img_enc(face):
    encoded={}
    
    faces = fr.load_image_file(face)
    face_enc = fr.face_encodings(faces)[0]
    encoded[face.split(".")[0]] = face_enc
    return list(encoded.keys()),list(encoded.values())
def check(face, test_face):
    face_known,face_enco_done=img_enc(face)
    
    face_loca = []
    face_enco = []
    face_name = []

    # to read  video and capture attendance

    img = cv2.imread(test_face)
    #small_frame = cv2.resize(frame,(0,0),fx = 0.25,fy = 0.25)
    rgb_frame = img  # small_frame#[:,:,::-1]
    if True:
        face_loca = fr.face_locations(rgb_frame)
        face_enco = fr.face_encodings(rgb_frame, face_loca)
        face_name = []
        for face_enc in face_enco:
            matches = fr.compare_faces(face_enco_done, face_enc)
            name = "Unknown_Unknown"
            face_distance = fr.face_distance(face_enco_done, face_enc)
            best_match = np.argmin(face_distance)

            if matches[best_match]:
                return True
            else:
                return False


def extract(face):
    imagePath = face
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30)
    )

    print("[INFO] Found {0} Faces.".format(len(faces)))

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_color = image[y:y + h, x:x + w]
      
        name = str(w)+str(h)+'_faces.jpg'
        cv2.imwrite(str(w) + str(h) + '_faces.jpg', roi_color)
    return name


def img_enc(face):
    encoded = {}

    faces = fr.load_image_file(face)
    face_enc = fr.face_encodings(faces)[0]
    encoded[face.split(".")[0]] = face_enc
    return list(encoded.keys()), list(encoded.values())


def result(id_img_path, selfie_img_path):
    res = False
    img = Image.fromarray(id_img_path,'RGB')
    img.save("id.jpg")
    img2 = Image.fromarray(selfie_img_path,'RGB')
    img2.save("selfie.jpg")
    r = ocr("id.jpg",reader)
    if r:
      extracted_facename = extract("id.jpg")
      res = check(extracted_facename,'selfie.jpg')
    return str(res)
    


def ocr(img,reader):

    
    result = reader.readtext(img)
    print(result)
    if result:
        print("True")
        return True
        
    return False
