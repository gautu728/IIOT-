from RPi.GPIO import GPIO
GPIO.setmode(GPIO.BCM)
pin=12
GPIO.setup(pin,GPIO.OUT)
GPIO.output(pin,True)