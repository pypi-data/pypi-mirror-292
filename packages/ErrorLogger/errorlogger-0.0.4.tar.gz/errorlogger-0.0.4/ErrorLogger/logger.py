import logging
import datetime
import requests
import configparser

class ErrorLogger:
    def __init__(self, config_file='config.ini'):
        # Read the config file
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Get the APM base URL
        self.apm_baseurl = config['DEFAULT']['apm_baseurl']
        
        # Configure the logger
        logging.basicConfig(filename='error_logs.log', level=logging.ERROR,
                            format='%(asctime)s %(levelname)s: %(message)s')
        self.logger = logging.getLogger()

    def collect_logs(self):
        try:
            response = requests.get(self.apm_baseurl)
            response.raise_for_status()
            logs = response.json()
            
            # Assuming logs are in a list format
            for log in logs:
                self.logger.error(f"Log: {log}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to collect logs: {e}")

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
