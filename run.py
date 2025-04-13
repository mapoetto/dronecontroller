
from flask import Flask, request, jsonify, render_template, make_response, session, redirect, url_for, send_from_directory, Response
from flask_httpauth import HTTPBasicAuth
from controllers.UAV_Controller import *
from controllers.UAV_Camera import *
from controllers.DroneKitController import *

import threading

import queue

import logging
import logging.handlers

# Coda thread-safe
log_queue = queue.Queue(-1)


autopilot_logger = logging.getLogger('autopilot')
dronekit_logger = logging.getLogger('dronekit')


# Handler che mette i log nella coda
queue_handler = logging.handlers.QueueHandler(log_queue)
autopilot_logger.addHandler(queue_handler)
dronekit_logger.addHandler(queue_handler)


file_handler1 = logging.FileHandler('autopilot.log', mode='a')  # 'a' per appendere, 'w' per sovrascrivere

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler1.setFormatter(formatter)

autopilot_logger.addHandler(file_handler1)
dronekit_logger.addHandler(file_handler1)

autopilot_logger.setLevel(logging.DEBUG)  # o DEBUG se vuoi tutto
dronekit_logger.setLevel(logging.DEBUG)  # o DEBUG se vuoi tutto


# Listener che gira in un thread separato
listener = logging.handlers.QueueListener(log_queue, file_handler1)
listener.start()


app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disabilita la cache per evitare che il browser carichi una versione vecchia del video


auth = HTTPBasicAuth()

# Credenziali di accesso
USERS = {
    "admin": "pydrone9"
}

CONFIG_FILE = 'DRONE_PARAMS.json'


flying_controller_thread = None



def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}  # Se il file non esiste o è vuoto, ritorna un dizionario vuoto
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Rotta per leggere tutta la configurazione e passarla al frontend
@app.route('/api/drone_params', methods=['GET'])
@auth.login_required
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/api/update_config', methods=['POST'])
@auth.login_required
def update_config():
    config = load_config()
    
    if not request.json:
        return jsonify({'status': 'error', 'message': 'Missing JSON body'}), 400

    # Aggiorna tutte le chiavi presenti nel JSON ricevuto
    for key, value in request.json.items():
        config[key] = value

    save_config(config)

    return jsonify({'status': 'success', 'updated': request.json})


@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username
    return None

@app.route('/')
@auth.login_required  # Protegge la rotta con autenticazione
def home():

    config = load_config()

    if mydrone:
        return render_template('index.html', config_list_parameters=config)
    return render_template('templates/error.html', connection=str(CONNECTION) ) 



@app.route('/console_updates')
@auth.login_required  # Protegge la rotta con autenticazione
def console_log():

    connection_string = "/dev/ttyACM0"
    baud_rate=115200

    connect(connection_string,baud_rate)

    return render_template('index.html')



@app.route('/api/takeoff')
@auth.login_required  # Protegge la rotta con autenticazione
def take_off():

    rtr = mydrone.arm_and_takeoff(int(DRONE_PARAMS["TAKE_OFF_ALTITUDE"]))

    return jsonify({'status': rtr})


@app.route('/log/autopilot')
@auth.login_required  # Protegge la rotta con autenticazione
def log_autopilot():

    last_rows = tail_optimized("autopilot.log", n=100, buffer_size=1024)
    last_rows.reverse()
    last_rows = "\n".join(last_rows)

    return last_rows, 200, {'Content-Type': 'text/plain'}



@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def tail_optimized(filename, n=10, buffer_size=1024):
    with open(filename, "rb") as f:
        f.seek(0, 2)  # Vai alla fine del file
        end_pos = f.tell()
        lines = []
        buffer = b""
        
        while len(lines) < n and f.tell() > 0:
            to_read = min(buffer_size, f.tell())
            f.seek(-to_read, 1)
            buffer = f.read(to_read) + buffer
            f.seek(-to_read, 1)
            lines = buffer.split(b"\n")
        
        return [line.decode("utf-8") for line in lines[-n:]]

'''
# Esempio di utilizzo
last_lines = tail_optimized("grande_file.txt", 10)
print("".join(last_lines))
'''

# Funzione che esegue arm_and_takeoff in un thread separato
def mydrone_connecting():
    mydrone.connect_vehicle()

if __name__ == "__main__":

    DRONE_PARAMS = load_config()

    CONNECTION = {}

    CONNECTION["connection_string"] = "/dev/ttyACM0"
    CONNECTION["baud_rate"] = 115200

    #mydrone = DroneKitController(CONNECTION["connection_string"],CONNECTION["baud_rate"])

    mydrone = DroneKitController(None,None,True)
    print("MyDrone Connecting...")
    
    mydrone.connect_vehicle()

    '''
    flying_controller_thread = threading.Thread(target=mydrone_connecting)
    flying_controller_thread.start()


    '''



    '''
    print(" Global Location: %s" % vehicle.location.global_frame)
    print(" Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
    print(" Local Location: %s" % vehicle.location.local_frame)
    print(" Attitude: %s" % vehicle.attitude)
    print(" Velocity: %s" % vehicle.velocity)
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)


    #Define callback for `vehicle.attitude` observer
    last_attitude_cache = None
    def attitude_callback(self, attr_name, value):
        # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
        # `self` - the associated vehicle object (used if a callback is different for multiple vehicles)
        # `value` is the updated attribute value.
        global last_attitude_cache
        # Only publish when value changes
        if value!=last_attitude_cache:
            print(" CALLBACK: Attitude changed to", value)
            last_attitude_cache=value

    print("\nAdd `attitude` attribute callback/observer on `vehicle`")     
    vehicle.add_attribute_listener('attitude', attitude_callback)


    # Demonstrate getting callback on any attribute change
    def wildcard_callback(self, attr_name, value):
        print(" CALLBACK: (%s): %s" % (attr_name,value))


    '''

    #print(str(mydrone.get_telemetry()))

    #app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000)

