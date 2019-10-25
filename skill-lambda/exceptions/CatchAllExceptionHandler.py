import logging
from ask_sdk_core.dispatch_components import AbstractExceptionHandler

logger = logging.getLogger(__name__)


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        message = "Something went wrong"
        return handler_input.response_builder.speak(message).response
