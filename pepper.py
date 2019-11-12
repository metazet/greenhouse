# -*- coding: utf-8 -*-
import time
import datetime

import RPi.GPIO as GPIO


class BaseSensorService(object):
    def __init__(self, sensor_pin, indicator_pin=None):
        self.sensor_pin = sensor_pin  # where the sensor is
        self.indicator_pin = indicator_pin  # where indicator is

        GPIO.setup(self.sensor_pin, GPIO.OUT)
        GPIO.output(self.sensor_pin, 0)
        GPIO.setup(self.indicator_pin, GPIO.OUT)
        GPIO.output(self.indicator_pin, 0)

    def enable(self):
        if not GPIO.input(self.sensor_pin):
            GPIO.output(self.sensor_pin, 1)
            if self.indicator_pin:
                GPIO.output(self.indicator_pin, 1)

    def disable(self):
        if GPIO.input(self.sensor_pin):
            GPIO.output(self.sensor_pin, 0)
            if self.indicator_pin:
                GPIO.output(self.indicator_pin, 0)

    def run(self):
        raise NotImplementedError

    def stop(self):
        # TODO: kill running thread
        pass


class TemperatureService(BaseSensorService):
    """ Service which control temperature: start it and stop on temperature threshold. """

    def __init__(self, sensor_pin, indicator_pin, temperature_threshold=28):
        """ temperature_threshold is a temperature when we should DISABLE heating. """

        super().__init__(sensor_pin, indicator_pin)
        self.temperature_threshold = temperature_threshold

    def get_current_temperature(self):
        """ Read from sensor and return current temperature. """
        return self.temperature_threshold

    def run(self):
        # TODO: convert to run in thread with possibility to stop
        while True:
            current_temperature = self.get_current_temperature()
            if current_temperature >= self.temperature_threshold:
                self.disable()
            else:
                self.enable()
            time.sleep(60*5)  # 5 minutes


class LightService(BaseSensorService):
    """ Service which control light: start it and stop on time. """

    def run(self):
        # TODO: convert to run in thread with possibility to stop
        while True:
            hour = datetime.datetime.utcnow().hour
            if hour >= 6 and hour <= 22:
                self.enable()
            else:
                self.disable()
            time.sleep(60*10)  # 10 minutes


class Controller(object):
    MAIN_INDICATOR_PIN = 2
    POWER_PIN = 5
    LIGHT_SENSOR_PIN = 3
    LIGHT_INDICATOR_PIN = 4
    TEMPERATURE_SENSOR_PIN = 6
    TEMPERATURE_INDICATOR_PIN = 7

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # init output and make them power=0
        GPIO.setup(self.MAIN_INDICATOR_PIN, GPIO.OUT)  # indicator that controller working
        GPIO.output(self.MAIN_INDICATOR_PIN, 1)

        # init input
        GPIO.setup(self.POWER_PIN, GPIO.IN)  # main power switch

        self.light_service = LightService(self.LIGHT_SENSOR_PIN, self.LIGHT_INDICATOR_PIN)
        self.temperature_service = TemperatureService(self.TEMPERATURE_SENSOR_PIN, self.TEMPERATURE_INDICATOR_PIN)

    def run(self):
        self.light_service.run()
        self.temperature_service.run()

        while True:
            if GPIO.input(self.POWER_PIN):
                self.light_service.run()
                self.temperature_service.run()
            else:
                self.light_service.stop()
                self.temperature_service.stop()
            time.sleep(1)
            continue


if __name__ == "__main__":
    controller = Controller()
    controller.run()
