from utils.validation import ValidationError, validation_response


class ExternalServiceError(RuntimeError):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def external_service_response(error):
    message = str(error)
    return {"status": "error", "message": message, "error": message}, error.status_code


def register_error_handlers(blueprint):
    blueprint.register_error_handler(ValidationError, validation_response)
    blueprint.register_error_handler(ExternalServiceError, external_service_response)
