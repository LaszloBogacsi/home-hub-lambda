from ask_sdk_core.dispatch_components import AbstractExceptionHandler


class SlotValueNotPresentException(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return 'SlotValueNotPresentException' in exception.__class__.__name__

    def handle(self, handler_input, exception):
        message = "Slot value not present"
        return handler_input.response_builder.speak(message).response
