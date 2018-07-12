import socket
import sys
import os
import re
import datetime
import psycopg2
import daemonocle
import logging
#import logging.handlers
import time
#import _thread

##############
# Object Class #
############

class MailClass:
    def AddMailFrom (self,Mailaddress):
        self.MailFrom.append(Mailaddress)
    def AddRcptTo (self,Mailaddress):
        self.RcptTo.append(Mailaddress)
    def CleanData (self):
        self.MailFrom = []
        self.RcptTo = []
        self.DateReceived = datetime.datetime.now()
        self.MailObject = ''
    def __init__(self):
        #self.ID = 0
        self.MailFrom = []
        self.RcptTo = []
        self.RemoteSender = ''
        self.RemoteSenderIP = ''
        self.DateReceived = datetime.datetime.now()
        self.MailObject = ''

###########
# Funzioni #
##########

def ServerStart():
    #Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server.settimeout(5.0)
#    Host = socket.gethostname()
#    WelcomeMsg = "220 " + Host + " ObjMail server ready\r\n"
#    HeloMsg = "250 Hello "
#    MailFromMsg = "250 Sender OK\r\n"
#    RcptToMsg = "250 Recipient OK\r\n"
#    DataMsg = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
#    QuitMsg = "221 Goodbye\r\n"
#    TooErrorMsg = "Troppi errori. Bye!\r\n"

    SocketOpen = False
    PID = os.getpid()

    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    Port = 25
    NrMaxConnection = 10

    DBCon = psycopg2.connect("host=127.0.0.1 dbname=objmail user=objmailadmin password=Garelli88")
    #print("Server avviato con il PID " + str(PID))
    logging.info("Server avviato con il PID " + str(PID))
    while SocketOpen == False:
        try:
            Server.bind((Host, Port))
            #print("Socket binding complete")
            logging.info("Socket binding complete")
            SocketOpen = True
        except :
            #print("Bind failed. Error Code : " + str(Message[0]) + "\r\nMessage :" + str(Message[1]))
            logging.error("Port 25 already used: impossible to open new socket. Will retry")
            time.sleep(10)
            

    Server.listen(NrMaxConnection)
    #print("Server is listening on port " + str(Port))
    logging.info("Server is listening on port " + str(Port))
    #print("creo l'oggetto mail")
    logging.debug("creo l'oggetto mail")
    MailRecived = MailClass()
    #print("so che spetto")
    logging.debug("so che spetto")
    #while True:
    #    Client, Address = Server.accept()
    #    _thread.start_new_thread(MailReciver(ServerSocket=Server, Mail=MailRecived, DataBaseConnection=DBCon, Client=Client, Address=Address))
    MailReciver(ServerSocket=Server, Mail=MailRecived, DataBaseConnection=DBCon)

def ServerStop(message, code):
    #Server.close()
    logging.info("Chiudo il socket del server")
    logging.debug(message)
    #Server.close()

#def MailReciver(ServerSocket, Mail, DataBaseConnection,Client,Address) :
def MailReciver(ServerSocket, Mail, DataBaseConnection) :
    ErrorCount = 0
    DataRecived = ''
    while True:
        #print("Sono nel ciclo infinito")
        logging.debug("Sono nel ciclo infinito")
        Client, Address = ServerSocket.accept()
        #Client.settimeout(1)
        ClientConnected = True
        #print('Connessione avvenuta da :', Address)
        logging.info('Connessione avvenuta da :', str(Address))
        Client.send(WelcomeMsg.encode())
        #print("Invio: " + WelcomeMsg)
        logging.debug("Invio: " + WelcomeMsg)

        Mail.RemoteSenderIP = Address[0]
        while DataRecived == '' and ErrorCount < 3 and ClientConnected == True:
            while not DataRecived.endswith('\r\n') and ClientConnected == True:
                Data = Client.recv(1024)
                DataRecived += Data.decode('utf-8')
                if bool(re.match('ehlo', DataRecived, re.I)):
                    try:
                        Caller = str(DataRecived.split(' ')[1])
                    except:
                        Caller = "Mister X\r\n"
                    Mail.RemoteSender = Caller
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    Client.send((HeloMsg + Caller).encode())
                    #print('Invio: ' + HeloMsg + Caller)
                    logging.debug('Invio: ' + HeloMsg + Caller)
                    DataRecived = ''
                elif bool(re.match('helo', DataRecived, re.I)):
                    try:
                        Caller = str(DataRecived.split(' ')[1])
                    except:
                        Caller = "Mister X\r\n"
                    Mail.RemoteSender = Caller
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    Client.send((HeloMsg + Caller).encode())
                    #print('Invio: ' + HeloMsg + Caller)
                    logging.debug('Invio: ' + HeloMsg + Caller)
                    DataRecived = ''
                elif bool(re.match('mail from:', DataRecived, re.I)):
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    AddressMail = re.findall(r'<(.*?)>', DataRecived, re.DOTALL)[0]
                    #print(AddressMail)
                    logging.debug(AddressMail)
                    Mail.AddMailFrom(str(AddressMail))
                    Client.send(MailFromMsg.encode())
                    #print('Invio: ' + MailFromMsg)
                    logging.debug('Invio: ' + MailFromMsg)
                    DataRecived = ''
                elif bool(re.match('rcpt to:', DataRecived, re.I)):
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    AddressMail = re.findall(r'<(.*?)>', DataRecived, re.DOTALL)[0]
                    #print(AddressMail)
                    logging.debug(AddressMail)
                    Mail.AddRcptTo(str(AddressMail))
                    Client.send(RcptToMsg.encode())
                    #print('Inivo: ' + RcptToMsg)
                    logging.debug('Inivo: ' + RcptToMsg)
                    DataRecived = ''
                elif bool(re.match('data', DataRecived, re.I)):
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    Client.send(DataMsg.encode())
                    #print('Invio: ' + DataMsg)
                    logging.debug('Invio: ' + DataMsg)
                    RealMail = ''
                    while not RealMail.endswith('\r\n.\r\n'):
                        DataRM = Client.recv(1024)
                        RealMail += DataRM.decode('utf-8')
                    Mail.MailObject = RealMail
                    logging.debug('La mail ricevuta e:\r\n' + RealMail)
                    DBCursor = DataBaseConnection.cursor()
                    # DBCursor.execute("INSERT INTO T_QueueRec.Mail (%s)", ("x"))
                    DBCursor.execute(
                        "INSERT INTO objmail.queuerec(mail) VALUES (ROW(%s, %s, %s, %s, %s, %s)) RETURNING queuerec.qid;",
                        (
                            Mail.MailFrom, Mail.RcptTo, Mail.RemoteSender,
                            Mail.RemoteSenderIP,
                            Mail.DateReceived, Mail.MailObject))
                    MailID = str(DBCursor.fetchone()[0])
                    DataBaseConnection.commit()
                    MailAcceptedMsg = "250 Mail accepted and queued for delivery with  ID " + MailID + "\r\n"
                    Client.send(MailAcceptedMsg.encode())
                    logging.info("Mail commitata nel db con ID: "+MailID)
                    DataRecived = ''
                    # DBCursor.close()
                    Mail.CleanData()

                elif bool(re.match('quit', DataRecived, re.I)):
                    #print('Ricevuto: ' + DataRecived)
                    logging.debug('Ricevuto: ' + DataRecived)
                    Client.send(QuitMsg.encode())
                    #print('Inivo: ' + QuitMsg)
                    logging.debug('Inivo: ' + QuitMsg)
                    DataRecived = ''
                    Client.close()
                    ClientConnected = False

                else:
                    ErrorCount += 1
                    #print(ErrorCount)
                    logging.debug("Error nr:"+str(ErrorCount))
                    #print('Non ho codificato questo comando: ' + DataRecived)
                    logging.info('Non ho codificato questo comando: ' + DataRecived)
                    DataRecived = ''

            #print(Mail.__dict__)
            logging.debug(Mail.__dict__)

############
# VARIABILI #
###########
#Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server.settimeout(5.0)
Host = socket.gethostname()
WelcomeMsg = "220 " + Host + " ObjMail server ready\r\n"
HeloMsg = "250 Hello "
MailFromMsg = "250 Sender OK\r\n"
RcptToMsg = "250 Recipient OK\r\n"
DataMsg = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
QuitMsg = "221 Goodbye\r\n"
TooErrorMsg = "Troppi errori. Bye!\r\n"

logging.basicConfig(
    filename='/var/log/objmail/ReceiverDaemon.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
#Handler= logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE","/var/log/objmail/ServerDaemon.log" ))
#LogFormat=logging.Formatter(logging.BASIC_FORMAT)
#Handler.setFormatter(LogFormat)
#Logger = logging.getLogger()
#Logger.setLevel(logging.INFO)
#Logger.addHandler(Handler)

####################
# CONNESSIONE DB #
###################




###############
# PROGRAMMA #
###############

if __name__ ==  '__main__' :
#    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server.settimeout(5.0)
#    Host = socket.gethostname()
#    WelcomeMsg = "220 " + Host + " ObjMail server ready\r\n"
#    HeloMsg = "250 Hello "
#    MailFromMsg = "250 Sender OK\r\n"
#    RcptToMsg = "250 Recipient OK\r\n"
#    DataMsg = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
#    QuitMsg = "221 Goodbye\r\n"
#    TooErrorMsg = "Troppi errori. Bye!\r\n"

    #ServerOpen()
    Servizio = daemonocle.Daemon(
        worker=ServerStart,
        shutdown_callback=ServerStop,
        pidfile='/var/run/ObjMail.pid',
    )
    Servizio.do_action(sys.argv[1])
    #Client.send(TooErrorMsg.encode())
#Server.close()
