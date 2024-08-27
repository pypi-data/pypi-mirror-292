
import logging
from cyclarity_sdk.platform_api.logger.models import ExecutionLog, LogInformation
from cyclarity_sdk.platform_api.connectors.mqtt_connector import MqttConnector


class ClarityStreamer(logging.Handler):
    def __init__(self, mqtt_com_manager: MqttConnector, execution_metadata):
        logging.Handler.__init__(self)
        self.mqtt_com_manager = mqtt_com_manager
        self.execution_metadata = execution_metadata

    def emit(self, record: logging.LogRecord) -> None:
        log_information = LogInformation(
            logger_name=record.name, log_level=record.levelno, time_stamp=record.created, message=record.message)
        execution_log = ExecutionLog(
            metadata=self.execution_metadata, data=log_information)
        try:
            self.mqtt_com_manager.publish_log(execution_log)
        except Exception as e:
            print("Failed publishing log topic, exception: " + str(e))
