# -*- coding: utf-8 -*-
import time
import datetime
import multiprocessing

import RPi.GPIO as GPIO


class BaseRelayService(object):
    def __init__(self, relay_pin, indicator_pin):
        """ Params are self-descriptive, here we just initialize pins.

        Usage:
            service = YourOwnService(2, 3)
            service.enable()  # for switch relay on
            service.disable()  # for switch relay off
        """
        self.relay_pin = relay_pin  # where the relay is
        self.indicator_pin = indicator_pin  # where the indicator is

        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, 0)
        GPIO.setup(self.indicator_pin, GPIO.OUT)
        GPIO.output(self.indicator_pin, 0)

    def enable(self):
        GPIO.output(self.relay_pin, 1)
        self.power_on_indicator()

    def disable(self):
        GPIO.output(self.relay_pin, 0)
        self.power_off_indicator()

    def power_on_indicator(self):
        GPIO.output(self.indicator_pin, 1)

    def power_off_indicator(self):
        GPIO.output(self.indicator_pin, 0)

    def run(self):
        raise NotImplementedError


class TemperatureService(BaseRelayService):
    """ Service which control temperature: start it and stop on temperature threshold. """

    def __init__(self, relay_pin, indicator_pin, sensor_pin, temperature_threshold=28):
        """  sensor_pin is a pin where we'll read temperature data.
             temperature_threshold is a temperature when we should DISABLE heating.
        """

        super().__init__(relay_pin, indicator_pin)

        self.temperature_threshold = temperature_threshold

        self.sensor_pin = sensor_pin
        GPIO.setup(self.sensor_pin, GPIO.IN)

    def get_current_temperature(self):
        """ Read from sensor and return current temperature. """
        # TODO: return real temperature from sensor
        return 25

    def run(self):
        while True:
            current_temperature = self.get_current_temperature()
            if current_temperature >= self.temperature_threshold:
                self.disable()
            else:
                self.enable()
            time.sleep(60*5)  # 5 minutes


class LightService(BaseRelayService):
    """ Service which control light: start it and stop on time. """

    def if_daylight_hours(self):
        hour = datetime.datetime.utcnow().hour
        return 6 <= hour <= 22

    def run(self):
        while True:
            if self.if_daylight_hours():
                self.enable()
            else:
                self.disable()
            time.sleep(60*10)  # 10 minutes


class Controller(object):
    """ Sensors controller which check main power and start/stop relay
        services (in separate processes).

        Usage:
            controller = Controller()
            controller.run()
        """

    MAIN_INDICATOR_PIN = 3
    POWER_PIN = 14
    LIGHT_RELAY_PIN = 27
    LIGHT_INDICATOR_PIN = 17
    TEMPERATURE_RELAY_PIN = 10
    TEMPERATURE_INDICATOR_PIN = 9
    TEMPERATURE_SENSOR_PIN = 11

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # init output and make them power=0
        GPIO.setup(self.MAIN_INDICATOR_PIN, GPIO.OUT)  # indicator that controller working

        # init input
        GPIO.setup(self.POWER_PIN, GPIO.IN)  # main power switch

        self.light_service = LightService(self.LIGHT_RELAY_PIN, self.LIGHT_INDICATOR_PIN)
        self.light_process = None

        self.temperature_service = TemperatureService(self.TEMPERATURE_RELAY_PIN,
                                                      self.TEMPERATURE_INDICATOR_PIN,
                                                      self.TEMPERATURE_SENSOR_PIN)
        self.temperature_process = None

    def run_services(self):
        """ Start sensor services in stand alone processes. """

        # start light process
        if self.light_process is None:
            self.light_process = multiprocessing.Process(target=self.light_service.run)
            self.light_process.start()

        # start temperature process
        if self.temperature_process is None:
            self.temperature_process = multiprocessing.Process(target=self.temperature_service.run)
            self.temperature_process.start()

    def stop_services(self):
        """ Kill processes. """

        # kill light process
        if self.light_process is not None and self.light_process.is_alive():
            self.light_process.terminate()
            self.light_process = None
            self.light_service.power_off_indicator()

        # kill temperature process
        if self.temperature_process is not None and self.temperature_process.is_alive():
            self.temperature_process.terminate()
            self.temperature_process = None
            self.temperature_service.power_off_indicator()

    def run(self):
        while True:
            if GPIO.input(self.POWER_PIN):
                GPIO.output(self.MAIN_INDICATOR_PIN, 1)
                self.run_services()
            else:
                GPIO.output(self.MAIN_INDICATOR_PIN, 0)
                self.stop_services()
            time.sleep(1)
            continue


if __name__ == "__main__":
    controller = Controller()
    controller.run()
