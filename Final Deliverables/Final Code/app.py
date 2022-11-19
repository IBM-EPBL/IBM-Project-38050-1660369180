from flask import Flask, render_template,redirect,url_for,request,Response
from moviepy.editor import VideoFileClip
import cv2
import speech_recognition as sr
from PIL import Image
import numpy as np
from skimage.transform import resize
from gtts import gTTS
import playsound
from keras.utils import image_utils as image
from keras.models import load_model

app=Flask(__name__)

vals=['A','B','C','D','E','F','G','H','I']
model=load_model('IBM.h5')

app.secret_key = "secret key"
arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
           'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','.']

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/audio_to_sign/')
def audio_to_sign():
    return render_template('SpeechtoSign.html')

@app.route('/audio', methods=['POST'])
def audio():
    r = sr.Recognizer()
    
    frameSize = (281, 363)
    out = cv2.VideoWriter('./static/uploads/output_video.mp4',cv2.VideoWriter_fourcc(*'DIVX'), 1, frameSize)
    with open('Speech/audio.mp3', 'wb') as f:
        f.write(request.data)
  
    with sr.AudioFile('Speech/audio.mp3') as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language='en-IN', show_all=True)
        print(text)
        
        try:
            for num, texts in enumerate(text['alternative']):
                transcript = texts['transcript'].lower()
                print(transcript)
                 
                break
            
        except:
            transcript = " Sorry!!!! Voice not Detected "

    for i in range(len(transcript)):
        if transcript[i] in arr:
            
            
            ImageAddress = 'L/'+transcript[i]+'.png'
            ImageItself = Image.open(ImageAddress)
            ImageNumpyFormat = np.asarray(ImageItself)
            img = cv2.imread(ImageAddress)
            out.write(img)
                
    out.release()
    videoFileClip=VideoFileClip("./static/uploads/output_video.mp4")
    videoFileClip.write_gif("./static/uploads/output_video.gif")
    videoFileClip.write_gif("./static/uploads/output_video1.gif")
        
    return str(transcript)

@app.route('/scrn', methods=['POST'])
def upload_video():
    r=sr.Recognizer()
    file=sr.AudioFile("Speech/audio.mp3")
    with file as source:
        audio_data = r.record(source)
    text = r.recognize_google(audio_data, language='en-IN', show_all=True)
    text=text['alternative']
    text=text[0]
    text=text['transcript']
    return render_template('stream.html', filename='output_video.gif',text=text)

@app.route('/display/<filename>')
def display_video(filename):
	
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/sign_to_audio/')
def sign_to_audio():
    return render_template('SigntoSpeech.html')

def gen():
    string = " "
    count = 90
    video = cv2.VideoCapture(0)
    while (video.isOpened()):
        ret, frame = video.read()
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        color_dict=(0,255,0)
        cv2.rectangle(frame,(24,24),(250 , 250),color_dict,2)
        copy=gray.copy()
        copy = copy[24:250,24:250]
        count = count + 1
        cv2.imwrite('static/image.jpg',copy)
        img = cv2.imread('static/image.jpg')
        img=resize(img,(64,64,1))
        img=image.img_to_array(img)
        img=np.expand_dims(img,axis=0)
        if(np.max(img)>1):
            img=img/255.0
        prediction=model.predict(img)
        prediction=np.argmax(prediction, axis=1)
        pred=vals[prediction[0]]
        print(pred)
        if(count == 200):
            count = 99
            prev= vals[prediction[0]]
            if(len(prev) == 0):
                string = string + "_"
                myobj = gTTS(text=string, lang="en", slow=False)
                myobj.save("Speech/sign.mp3")
                
                
            else:
                string = string + prev
                myobj = gTTS(text=string, lang="en", slow=False)
                myobj.save("Speech/sign.mp3")
                

        cv2.putText(frame, pred, (24, 14),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)
        cv2.putText(frame, string, (275, 50),cv2.FONT_HERSHEY_SIMPLEX,0.8,(200,200,200),2)
        if not ret:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
     return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/redirect')
def delet():
    video = cv2.VideoCapture(0)
    video.release()
    return render_template("index.html")

@app.route('/play')
def play():
    playsound.playsound("Speech/sign.mp3", True)
    return render_template("SigntoSpeech.html")

@app.route('/alp')
def alp():
    
    return render_template("Alphabet.html")

if __name__ == "__main__":
    app.run(debug=True)