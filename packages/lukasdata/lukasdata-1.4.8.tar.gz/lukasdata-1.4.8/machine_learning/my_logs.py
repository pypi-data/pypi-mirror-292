import logging
from datetime import datetime


class my_logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
    def setup_logs(self,filename):
        path="C:/Users/lukas/Desktop/bachelor/models/logs/"+filename
        logging.basicConfig(filename=path, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #logger = logging.getLogger('ModelLogger')
    def log_parameters(self,parameters):
        self.info(f'Parameters: {parameters}')

    def log_performance(self,performance):
        self.info(f'Performance: {performance}')



def build_logger(name):
    logging.setLoggerClass(my_logger)
    logger=logging.getLogger(name)
    file_name=name+".log"
    logger.setup_logs(file_name)
    return logger














