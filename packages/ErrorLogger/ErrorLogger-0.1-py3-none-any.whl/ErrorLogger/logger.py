import logging
import datetime

class ErrorLogger:
    def __init__(self, log_file='error_logs.log'):
        logging.basicConfig(filename=log_file, level=logging.ERROR, 
                            format='%(asctime)s %(levelname)s: %(message)s')
        self.logger = logging.getLogger()

    def log_exception(self, exception: Exception, message: str = None):
        error_message = message if message else str(exception)
        self.logger.error(f"Exception: {error_message}")
        self.logger.error(f"Type: {type(exception).__name__}")
        self.logger.error(f"Details: {str(exception)}")
        self.logger.error(f"Timestamp: {datetime.datetime.now()}")

def capture_exception(logger: ErrorLogger, message: str = None):
    def wrapper(func):
        def inner_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(e, message)
                raise e  # Re-raise the exception after logging it
        return inner_function
    return wrapper
