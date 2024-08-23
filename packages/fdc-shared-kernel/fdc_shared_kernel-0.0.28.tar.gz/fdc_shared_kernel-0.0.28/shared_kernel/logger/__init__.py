import logging
import os


class Logger:
    """
    A singleton logger class that ensures only one logger instance is created.
    This logger supports both console and file logging.

    Attributes:
        _instance (Optional[Logger]): The single instance of the logger.
    """

    _instance = None

    def __new__(cls, name=None):
        """
        override __new__ to ensure singleton pattern.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize(name=name)
        return cls._instance

    def _initialize(self, name=None, log_file: str = "fdc_app_logs.log"):

        self.logger = logging.getLogger(name if name else __name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(module)s - %(levelname)s - %(message)s"
        )
        self.log_file = log_file

        # ensure handlers are configured only once
        if not self.logger.handlers:
            self.configure_logger()

    def configure_logger(self):
        """
        Configures logger with stream and file handlers.
        """
        self.add_stream_handler()
        self.add_file_handler(log_file=self.log_file)

    def add_stream_handler(self):
        """
        Adds a stream handler to the logger.
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.logger.level)
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

    def add_file_handler(self, log_file, log_directory="./logs"):
        """
        Adds a file handler to the logger.
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        file_handler = logging.FileHandler(os.path.join(log_directory, log_file))
        file_handler.setLevel(self.logger.level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)
