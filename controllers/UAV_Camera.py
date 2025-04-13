import cv2
import os
import argparse

'''
from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference
'''

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, _ = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0, x1, y1 = int(bbox.xmin), int(bbox.ymin), int(bbox.xmax), int(bbox.ymax)
        percent = int(100 * obj.score)
        label = '{}% {}'.format(percent, labels.get(obj.id, obj.id))
        cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(cv2_im, label, (x0, y0+30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    return cv2_im


def find_working_camera():
    for i in range(5):  # Prova i primi 5 indici di videocamera
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
    return None  # Nessuna webcam trovata

def generate_frames():
    cam_index = find_working_camera()
    if cam_index is None:
        print("Errore: Nessuna webcam disponibile!")
        return

    cap = cv2.VideoCapture(cam_index)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

'''
def generate_frames():
    
    default_model_dir = '../../drone/coral/pycoral/examples-camera/all_models'
    default_model = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    default_labels = 'coco_labels.txt'
    
    interpreter = make_interpreter(os.path.join(default_model_dir, default_model))
    interpreter.allocate_tensors()
    labels = read_label_file(os.path.join(default_model_dir, default_labels))
    inference_size = input_size(interpreter)
    

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, 0.1)[:3]
        frame = append_objs_to_img(frame, inference_size, objs, labels)
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
'''
