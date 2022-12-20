from managers.email_queue_manager import EmailQueueManager
import sys
import logging
#
if __name__ == '__main__':
    logging.basicConfig(filename='application_log.txt', filemode='a', encoding='utf-8', 
    level=logging.DEBUG, format='%(asctime)s.%(msecs)03d|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        EmailQueueManager()
    except KeyboardInterrupt:
        logging.warning("User stopped the process manually!")
    except Exception as e:
        logging.error('index | Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
