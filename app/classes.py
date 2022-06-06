import sys
import os
import json
import logging
import traceback
from datetime import datetime
from settings import settings


class _Error(Exception):
    def __init__(self, exception, error_type, file_error, line_error):
        self.exception = exception.args[0]
        self.error_type = error_type
        self.line_error = line_error
        self.file_error = file_error
        self.timestamp = datetime.now()

    def returnError(self):
        data_set = {
            "timestamp": str(self.timestamp),
            "message": self.exception,
            "file": f"{self.file_error} on line {self.line_error}",
        }

        json_dump = json.dumps(data_set)
        json_object = json.loads(json_dump)
        if settings.complete_stack_error:
            json_object["complete_stack_error"] = str(traceback.format_exc())
        return json_object
