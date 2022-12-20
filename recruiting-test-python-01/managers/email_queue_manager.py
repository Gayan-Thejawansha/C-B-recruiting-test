from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
import time
import random
import sys
import multiprocessing as mp
from models.generator.email import Email
import logging
import csv
import matplotlib.pyplot as plt




class EmailQueueManager:
    __queue = []

    def __init__(self):
        # !!! You can't edit this section 11:14
        # This var "self.__queue" is the variable that save the current queue of emails
        self.__queue = self.__generate_emails(
            quantity=10
        )

        self.__queue_processor()

    def __queue_processor(self):

        try:        
            while True:
                prevCount = len(self.__queue)
                start = time.time()
                self.__queue += self.__generate_emails(
                    quantity= random.randint(1, 10)
                )
                addedCount =  len(self.__queue) - prevCount
                sentCount = 0
                with mp.Manager() as manager:
                    retryQ = manager.dict()
                    PriorityQ = manager.dict()
                    pendingQ = manager.dict()

                    for idx, email in enumerate(self.__queue):

                        if email["status"] == "sent":
                            del self.__queue[idx]
                            sentCount += 1
                            continue

                        if email["attempts"] > 0:
                            retryQ[idx] = email

                        elif email["priority"] > 1:
                            PriorityQ[idx] = email

                        else: 
                            pendingQ[idx] = email


                    retryQlist = list(retryQ.items())
                    PriorityQlist = list(PriorityQ.items())
                    pendingQlist = list(pendingQ.items())
                    logging.info(f'CREATEEMAIL|Sent Email Count:{sentCount}|'
                                +f'Added Email Count:{addedCount}|'
                                +f'All Pending Email Count:{len(self.__queue)}|'
                                +f'Pending Retry Email Count:{len(retryQlist)}|'
                                +f'Pending Priority Email Count:{len(PriorityQlist)}')

                    with ThreadPool(processes=8) as pool:
                        pool.imap_unordered(self.__emailCollectionProcessor, PriorityQlist,)
                        pool.imap_unordered(self.__emailCollectionProcessor, retryQlist,)
                        pool.imap_unordered(self.__emailCollectionProcessor, pendingQlist,)
                        pool.close()
                        pool.join()

                end = time.time()
                print(f'pending emails to send: {len(self.__queue)} | addedCount: {addedCount} | sentCount: {sentCount} | excecution_time: {round(end - start, 3)}' )
                #logging.log()
                time.sleep(0.5)

        except KeyboardInterrupt:
            logging.warning("User stopped the process manually!")
            pool.terminate()
            pool.join()
        except Exception as e:
            pool.terminate()
            pool.join()
            logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        finally:
            pool.close()
            pool.join()
            self.__plotter('application_log.txt')


    def __plotter(self, data):
        with open(data) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='|')
            dataStream = []

            for row in csv_reader:
                if row[2] == 'INFO':
                    dataStream.append(row)
            
            startTime = datetime.strptime(dataStream[0][0], '%Y-%m-%d %H:%M:%S.%f') 
            endTime = datetime.strptime(dataStream[len(dataStream)-1][0], '%Y-%m-%d %H:%M:%S.%f') 
            curTime = startTime
            curPos  = 0
            times = []
            addedCountList = []
            excecutedCountList = []
            failedCountList = []
            while curTime < endTime:
                nextTime = curTime + timedelta(milliseconds=500)
                addedCount = 0
                excecutedCount = 0
                failedCount =0

                while curPos< len(dataStream) and datetime.strptime(dataStream[curPos][0], '%Y-%m-%d %H:%M:%S.%f') < nextTime :
                    if dataStream[curPos][3] == 'CREATEEMAIL':
                        addedCount = addedCount + int((dataStream[curPos][5]).split(':')[1])
                    if dataStream[curPos][3] == 'SENDEMAIL':
                        excecutedCount = excecutedCount + 1
                        if  dataStream[curPos][8] == 'After Status:pending':
                             failedCount = failedCount + 1                 
                    curPos +=1
                times.append(curTime)
                addedCountList.append(addedCount)
                excecutedCountList.append(excecutedCount)
                failedCountList.append(failedCount)

                curTime = nextTime
            plt.style.use('seaborn-whitegrid')
            fig, ax = plt.subplots(3)
            ax[0].plot(times, addedCountList, label="Added Count", color='b')
            ax[1].plot(times, excecutedCountList, label="Excecuted Count",color='g')
            ax[2].plot(times, failedCountList, label="Failed Count",color='r')
            fig.tight_layout()
            ax[0].title.set_text("Added Count")
            ax[1].title.set_text("Excecuted Count")
            ax[2].title.set_text("Failed Count")          
            plt.grid(True,color='k')
            plt.savefig("summery.jpeg")
            

            

    def __emailCollectionProcessor(self, emailObject):

        try:
            response = self.__send_email(
                email=emailObject[1]
            )
            logging.info(f'SENDEMAIL|Email ID:{response["email"]["id"]}|'
            +f'Number of Attempts:{response["email"]["attempts"]}|'
            +f'Priority:{response["email"]["attempts"] > 1}|'
            +f'Prev. Status:{emailObject[1]["status"]}|'
            +f'After Status:{response["email"]["status"]}')
            self.__queue[emailObject[0]] = response["email"] 
            return

        except KeyboardInterrupt:
            logging.warning("User stopped the process manually!")
            return
        except Exception as e:
            logging.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            return        


    # !!! You can't edit this method
    # This method generate an array with many emails that you should send after.
    def __generate_emails(self, quantity):
        return Email().generate_many(quantity=quantity)

    # !!! You can't edit this method
    # This method is used to send fake email, this method could delay from 0 to 1 second by every send process.
    def __send_email(self, email):
        time.sleep(random.uniform(0, 1))

        error = random.randint(0, 1)

        if error == 1:
            email["attempts"] += 1

        response = {
            "status": "sent" if error == 0 else "error",
            "email": {
                **email,
                **{
                    "status": "pending" if error == 1 else "sent",
                }
            },
        }

        print(
            f'[status:{response["email"]["status"]}] ' +
            f'email:{response["email"]["id"]} ' +
            f'attempts:{response["email"]["attempts"]} '
        )

        return response
