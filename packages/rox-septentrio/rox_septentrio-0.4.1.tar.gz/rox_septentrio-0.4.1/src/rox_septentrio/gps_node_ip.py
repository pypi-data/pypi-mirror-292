#!/usr/bin/env python3
"""
GPS node. Reads NMEA data from a socket, parses it and publishes to MQTT
Includes robust socket connection handling, complete type hints, and full stack traces on exceptions.

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import os
import logging
import time
import traceback
from typing import Dict, Type, Union, Optional
import coloredlogs  # type: ignore
import socket
import paho.mqtt.client as mqtt
from rox_septentrio import config
from rox_septentrio import nmea
import orjson

# Setup logging configuration
LOG_FORMAT: str = "%(asctime)s.%(msecs)03d  %(message)s"
LOGLEVEL: str = os.environ.get("LOGLEVEL", "INFO").upper()

coloredlogs.install(level=LOGLEVEL, fmt=LOG_FORMAT)

log: logging.Logger = logging.getLogger("gps_node")


def connect_socket(gps_cfg: config.GpsConfig) -> socket.socket:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((gps_cfg.ip_host, gps_cfg.ip_port))
    log.info(f"Connected to GPS server at {gps_cfg.ip_host}:{gps_cfg.ip_port}")
    return sock


def main() -> None:
    log.info("Starting GPS node over IP")
    mqtt_cfg: config.MqttConfig = config.MqttConfig()
    gps_cfg: config.GpsConfig = config.GpsConfig()

    topic_map: Dict[Type[Union[nmea.PositionData, nmea.HeadingData]], str] = {
        nmea.PositionData: mqtt_cfg.position_topic,
        nmea.HeadingData: mqtt_cfg.direction_topic,
    }

    # Initialize MQTT client
    log.info(f"Connecting to MQTT broker at {mqtt_cfg.host}:{mqtt_cfg.port}")
    client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    client.connect(mqtt_cfg.host, mqtt_cfg.port, 60)

    while True:
        try:
            log.info(f"Connecting to GPS server at {gps_cfg.ip_host}:{gps_cfg.ip_port}")
            with connect_socket(gps_cfg) as sock:
                while True:
                    data: bytes = sock.recv(1024)
                    if not data:
                        log.warning("No data received. Reconnecting...")
                        break

                    decoded_data: str = data.decode("utf-8")
                    for line in decoded_data.split("\n"):
                        line = line.strip()
                        if not line:
                            continue

                        log.debug(f"{line=}")
                        try:
                            msg: Optional[
                                Union[nmea.PositionData, nmea.HeadingData]
                            ] = nmea.parse(line)
                            if msg is not None:
                                log.debug(f"{msg=}")
                                json_data: bytes = orjson.dumps(msg.to_dict())
                                topic: str = topic_map[type(msg)]
                                client.publish(topic, json_data)
                        except Exception as e:
                            log.warning(f"Could not parse '{line}': {e}")
                            log.error("Full stack trace:")
                            log.error(traceback.format_exc())

        except KeyboardInterrupt:
            log.info("GPS node interrupted by user")
            break
        except Exception as e:
            log.exception(f"Error: {e}", exc_info=True)
            log.info("Attempting to reconnect in 5 seconds...")
            time.sleep(5)

    client.loop_stop()


if __name__ == "__main__":
    main()
