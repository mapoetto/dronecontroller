'''
from flask import render_template, Response
from app.controllers.UAV_Controller import *
from app.controllers.UAV_Camera import *

from app.controllers.DroneKitController import *




global mydrone

print("------------ Starting routes.py")

mydrone = DroneKitController(CONNECTION["connection_string"],CONNECTION["baud_rate"])
print("------------ mydrone created")

if mydrone.connect_vehicle() == True:
    print("------------ Connection to the vehicle DONE !")
else:
    print("------------ Problem with vehicle connection !")

print("------------ Trying to get TELEM....")
print(str(mydrone.get_telemetry()))



def init_routes(app):
    
    global mydrone

    @app.before_request
    def esegui_prima_di_tutto():

        global mydrone

        print("------------ Starting routes.py")

        mydrone = DroneKitController(CONNECTION["connection_string"],CONNECTION["baud_rate"])
        print("------------ mydrone created")

        if mydrone.connect_vehicle() == True:
            print("------------ Connection to the vehicle DONE !")
        else:
            print("------------ Problem with vehicle connection !")

        print("------------ Trying to get TELEM....")
        print(str(mydrone.get_telemetry()))
    


    @app.route('/')
    def home():

        print("home")
        if mydrone is not None:
            return render_template('index.html', )
        return render_template('error.html', connection=str(CONNECTION) ) 



    @app.route('/console_updates')
    def console_log():

        connection_string = "/dev/ttyACM0"
        baud_rate=115200

        connect(connection_string,baud_rate)

        return render_template('index.html')

    @app.route('/video')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



    @app.route('/users')
    def users():
        return get_users()
'''
