# coding:utf8
"""

"""
import cv2
import time, random, json
from random import choice
from datetime import datetime as dt
from flask import request, send_from_directory
from flask import Flask, render_template, Response, make_response
# from camera import VideoCamera
from video import VideoCamera


app = Flask(__name__)
# 全局变量
cam = VideoCamera()
start_time = dt.now()


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/')
def index():
    tab1_header_class = "active"
    tab1_content_class = " in active"
    tab2_header_class = " "
    tab2_content_class = " "
    return render_template('index.html', **locals())

@app.route('/tab1')
def enter_tab1():
    tab1_header_class = "active"
    tab1_content_class = " in active"
    tab2_header_class = " "
    tab2_content_class = " "
    return render_template('index.html', **locals())


@app.route('/tab2')
def enter_tab2():
    tab2_header_class = "active"
    tab2_content_class = " in active"
    tab1_header_class = " "
    tab1_content_class = " "
    return render_template('index.html', **locals())

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


'''
@app.route('/video_feed')
def video_feed():
    """
    将视频实时返回
    {{url_for('video_feed')}}
    /img/demo.jpg
    """
    return Response(gen(cam), mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')
'''

fname = 'v1.png'

@app.route('/video_feed')
def video_feed():
    """
    将视频实时返回
    {{url_for('video_feed')}}
    /img/demo.jpg
    """
    global fname
    if fname == 'v1.png':
        fname = 'v2.png'
    else:
        fname = 'v1.png'

    frame = cv2.imencode('.jpg', cv2.imread('img/' + fname))[1].tostring()
    img = (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    return Response(img, mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video/video_home.html')
def video_home():
    return render_template('video_home.html')


@app.route('/live-data')
def live_data():
    # Create a PHP array and echo it as JSON
    data = [time.time() * 1000, random.random() * 100]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/frame_test')
def frame_test():
    return render_template('frame_test.html')

@app.route('/frame_a')
def frame_a():
    return render_template('video_home.html')

@app.route('/frame_b')
def frame_b():
    return render_template('tab2.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)