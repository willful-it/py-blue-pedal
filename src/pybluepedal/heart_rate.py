import logging
import queue

from bluepy.btle import DefaultDelegate, Peripheral

from byte_ops import check_bit_l2r

logger = logging.getLogger("HeartRateService")


class HeartRateService:
    UUID = "0000180d"
    CHARACTERISTIC_MEASUREMENT = "00002a37"

    def __init__(self, peripheral: Peripheral):
        self.__peripheral = peripheral
        self.__service = self.__peripheral.getServiceByUUID(
            HeartRateService.UUID)

    def start_notifications(self, delegate: DefaultDelegate):
        """Starts the notifications for the characteristic measurement"""

        logger.debug("starting notification")

        self.__peripheral.setDelegate(delegate)

        characteristics = self.__service.getCharacteristics(
            forUUID=HeartRateService.CHARACTERISTIC_MEASUREMENT)

        characteristic = characteristics[0]

        resp = self.__peripheral.writeCharacteristic(
            characteristic.getHandle() + 1, b"\x01\x00", True)

        logger.debug(f"notification started: {resp}")


class HeartRateDelegate(DefaultDelegate):
    def __init__(self, producer_queue: queue.Queue):
        DefaultDelegate.__init__(self)

        self.__producer_queue = producer_queue

    def handleNotification(self, cHandle, data):
        logger.debug(f"handing notification {cHandle} {data}")

        values = list(bytearray(data))
        flag_field = values[0]
        logger.debug(f"flag field {bin(flag_field)}")

        if not check_bit_l2r(flag_field, 0):
            data = {"type": cHandle, "value": values[1]}
        else:
            data = {"type": cHandle, "value": values[1:]}

        self.__producer_queue.put(data)
        logger.debug(f"added to queue {data}")


# print("Services...")
# for svc in dev.services:
#     print("---------------------------")
#     uuid = str(svc.uuid)
#     name = str(svc.uuid.getCommonName())
#     print(uuid, name)

#     print(f"Characteristics for {name}")
#     sensor = btle.UUID(uuid)

#     sensor_service = dev.getServiceByUUID(sensor)
#     for ch in sensor_service.getCharacteristics():
#         print(str(ch), str(ch.uuid), str(ch))
#         try:
#             val = ch.read()
#             print("   > Raw value", str(val), binascii.b2a_hex(val))
#         except Exception as e:
#             print("   > Error")
#             pass
#             # print(e)
