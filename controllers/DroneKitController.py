from dronekit import connect, VehicleMode, LocationGlobalRelative
import json
import time
import dronekit_sitl
import logging
import queue
import logging.handlers
import threading
from typing import Dict, Any, Callable, Optional, List


class HeavyTaskThread(threading.Thread):

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._results = None
        self._is_running = False

    def run(self):
        self._is_running = True
        try:
            self._results = self._target(*self._args, **self._kwargs)
        finally:
            self._is_running = False

    def check(self):
        """Check if the thread is still running."""
        return self.is_alive()

    def get_results(self):
        """Retrieve the results after the task completes."""
        if self._is_running:
            raise Exception("Task is still running, results are not available yet.")
        return self._results


class DroneKitController:
    def __init__(self, connection_string,baud_rate,sitl=False):


        self.flying_controller_thread = None


        self.connection_string = connection_string
        self.baud_rate = baud_rate
        self.vehicle = None
        self.sitl_mode = sitl

        if self.sitl_mode:
            self.my_sitl = dronekit_sitl.start_default() 


    #Callback function for "any" parameter
    def any_parameter_callback(self, attr_name, value):
        print("attr_name->"+str(attr_name)+" value->"+str(value))



    def execute_task(self, func_name: Callable, args=None):
        if self.flying_controller_thread and self.flying_controller_thread.check():
            return "Task is busy..."

        if args:
            self.flying_controller_thread = HeavyTaskThread(func_name, *args)
        else:
            self.flying_controller_thread = HeavyTaskThread(func_name)

        self.flying_controller_thread.start()
        return "Task avviato"




    def connect_vehicle(self):
        self.execute_task(func_name=self.connect_vehicle_bloccante)

    def connect_vehicle_bloccante(self):
        """Connette il drone e ritorna l'oggetto vehicle."""
        try:
            if self.sitl_mode:
                print("CONNECTING TO THE VEHICLE in SITL Mode")
                print("Connecting to vehicle on: %s" % (self.my_sitl.connection_string(),))
                #self.vehicle = connect(self.my_sitl.connection_string(), wait_ready=True)
                self.vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)
                print(".>"+str(vehicle))
                    

                #Add observer for the vehicle's any/all parameters parameter (note wildcard string ``'*'``)
                vehicle.parameters.add_attribute_listener('*', any_parameter_callback)

            else:
                self.vehicle = connect(self.connection_string, baud=self.baud_rate, wait_ready=True)
            return self.vehicle
        except Exception as e:
            return f"Errore di connessione: {str(e)}"
    
    def get_telemetry_bloccante(self):
        """Restituisce la telemetria del drone in formato JSON."""
        if self.vehicle is None:
            return json.dumps({"error": "Drone non connesso"})
        
        telemetry_data = {
            "global_location": self.vehicle.location.global_frame, #posizione assoluta del drone, nel mondo
            "local_location": self.vehicle.location.local_frame ,
            "attitude": str(self.vehicle.attitude), #contiene yaw,pitch,roll
            "relative_location": self.vehicle.location.global_relative_frame , #coordinate relative al punto di arming/decollo
            "gps": self.vehicle.gps_0 ,
            "latitude": self.vehicle.location.global_frame.lat,
            "longitude": self.vehicle.location.global_frame.lon,
            "altitude": self.vehicle.location.global_frame.alt,
            "velocity": self.vehicle.velocity,
            "heading": self.vehicle.heading, #l'orientamento del drone rispetto al Nord
            "battery_voltage": self.vehicle.battery.voltage,
            "battery_current": self.vehicle.battery.current,
            "battery_level": self.vehicle.battery.level,
            "mode": self.vehicle.mode.name,
            "armed": self.vehicle.armed
        }

        return json.dumps(telemetry_data, indent=4)
    



    def arm_and_takeoff(self,target_altitude):

        return self.execute_task(func_name=self.arm_and_takeoff_bloccante,  args=(target_altitude,))

    def arm_and_takeoff_bloccante(self, target_altitude):
        """Arma il drone e lo fa decollare all'altitudine desiderata."""
        if self.vehicle is None:
            return "Drone non connesso"
        
        print("Arming motors...")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        while not self.vehicle.armed:
            print("Waiting for arming...")
            time.sleep(1)
        
        print("Taking off!")
        self.vehicle.simple_takeoff(target_altitude)
        
        while True:
            print(f"Altitude: {self.vehicle.location.global_relative_frame.alt}")
            if self.vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
                print("Target altitude reached")
                break
            time.sleep(1)

        return "Takeoff complete"
    
    def land_bloccante(self):
        """Comanda il drone per atterrare."""
        if self.vehicle is None:
            return "Drone non connesso"
        
        print("Landing...")
        self.vehicle.mode = VehicleMode("LAND")
        return "Landing initiated"
    
    def goto_bloccante(self, lat, lon, alt):
        """Sposta il drone a una posizione specifica."""
        if self.vehicle is None:
            return "Drone non connesso"
        
        print(f"Going to {lat}, {lon}, {alt}")
        point = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(point)
        return f"Navigating to {lat}, {lon}, {alt}"
    
    def close_connection_bloccante(self):
        """Chiude la connessione con il drone."""
        if self.vehicle is not None:

            if sitl_mode:
                self.my_sitl.stop()

            self.vehicle.close()
            self.vehicle = None
            return "Connessione chiusa"
        return "Nessuna connessione da chiudere"