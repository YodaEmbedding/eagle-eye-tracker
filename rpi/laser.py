import pigpio
from time import sleep

class Laser:

    def __init__(self, pigpiod, ena_pin):
        self.pi = pigpiod

        self.ena_pin = ena_pin
        self.pi.set_mode(self.ena_pin, pigpio.OUTPUT)

        
    def laser_on(self):
        self.pi.write(self.ena_pin, 1)
        
    def laser_off(self):
        self.pi.write(self.ena_pin, 0)
        
if __name__ == '__main__':
    pi = pigpio.pi()
    if not pi.connected:
        exit()
    
    laser = Laser(pi, 23)
    
    try:
        while True:
            laser.laser_on()
            sleep(2)
            laser.laser_off()
            sleep(2)
            
    except KeyboardInterrupt:
        print("exit")
    finally:
        laser.laser_off()
