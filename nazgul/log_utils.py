import logging
import json
import socket

from flask import has_request_context, request

HOSTNAME = socket.gethostname()


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(JsonLogFormatter())

    logger.addHandler(stream_handler)


def default_logger():
    return logging.getLogger("nazgul")


class JsonLogFormatter(logging.Formatter):
    LOGGING_FORMAT_VERSION = "2.0"

    # Map from Python logging to Syslog severity levels
    SYSLOG_LEVEL_MAP = {
        50: 2,  # CRITICAL
        40: 3,  # ERROR
        30: 4,  # WARNING
        20: 6,  # INFO
        10: 7,  # DEBUG
    }

    # Syslog level to use when/if python level isn't found in map
    DEFAULT_SYSLOG_LEVEL = 7

    def __init__(self, format=None, datefmt=None, logger_name="default"):
        super(JsonLogFormatter, self).__init__(format, datefmt)
        self.logger_name = logger_name

    def format(self, record):
        out = dict(
            Timestamp=int(record.created * 1e9),
            Type=record.name,
            Logger=self.logger_name,
            Hostname=HOSTNAME,
            EnvVersion=self.LOGGING_FORMAT_VERSION,
            Severity=self.SYSLOG_LEVEL_MAP.get(
                record.levelno, self.DEFAULT_SYSLOG_LEVEL
            ),
            Pid=record.process,
        )

        fields = dict()

        if record.args:
            fields["msg"] = record.getMessage()
        else:
            fields = record.msg

        if has_request_context():
            request_details = {}
            request_details["url"] = request.url
            request_details["method"] = request.method
            request_details["user"] = (
                request.authorization.get("username")
                if request.authorization
                else "anonymous"
            )
            request_details["agent"] = request.user_agent.string
            if request.form:
                request_details["params"] = request.form
            fields["request"] = request_details

        out["Fields"] = fields

        return json.dumps(out)
