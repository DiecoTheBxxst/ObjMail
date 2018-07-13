import socket
import sys
import os
import re
import datetime
import psycopg2
import time

sys.path.insert(0, '/opt/objmail/Lib/')
from GeneralLib import *

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

#############
# VARIABLES #
############
#Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server.settimeout(5.0)
#Host = socket.gethostname()
#WelcomeMsg = "220 " + Host + " ObjMail server ready\r\n"
#HeloMsg = "250 Hello "
#MailFromMsg = "250 Sender OK\r\n"
#RcptToMsg = "250 Recipient OK\r\n"
#DataMsg = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
#QuitMsg = "221 Goodbye\r\n"
#TooErrorMsg = "Troppi errori. Bye!\r\n"

##############
# FUNCTIONS #
#############

def ServerStart():
    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server.settimeout(5.0)
    Host = socket.gethostname()
    WelcomeMsg = "220 " + Host + " ObjMail server ready\r\n"
    HeloMsg = "250 Hello "
    MailFromMsg = "250 Sender OK\r\n"
    RcptToMsg = "250 Recipient OK\r\n"
    DataMsg = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
    QuitMsg = "221 Goodbye\r\n"
    TooErrorMsg = "Troppi errori. Bye!\r\n"

    SocketOpen = False
    PID = os.getpid()
    Port = 25
    NrMaxConnection = 10

    #DBCon = psycopg2.connect("host=127.0.0.1 dbname=objmail user=objmailadmin password=Garelli88")
    DBCon = psycopg2.connect("host=127.0.0.1 dbname=objmail user=objmailadmin")
    Logger('info',"Server avviato con il PID " + str(PID))
    while SocketOpen == False:
        try:
            Server.bind((Host, Port))
            Logger('info',"Socket binding complete")
            SocketOpen = True
        except :
            Logger('error',"Port 25 already used: impossible to open new socket. Will retry")
            time.sleep(10)
            

    Server.listen(NrMaxConnection)
    Logger('info',"Server is listening on port " + str(Port))
    Logger('debug',"creo l'oggetto mail")
    Mail = MailClass()
    Logger('debug',"so che spetto")
    #while True:
    #    Client, Address = Server.accept()
    #    _thread.start_new_thread(MailReciver(ServerSocket=Server, Mail=MailRecived, DataBaseConnection=DBCon, Client=Client, Address=Address))
    #MailReciver(ServerSocket=Server, Mail=MailRecived, DataBaseConnection=DBCon)
    ErrorCount = 0
    DataRecived = ''
    while True:
        Logger('debug',"Sono nel ciclo infinito")
        Client, Address = Server.accept()
        ClientConnected = True
        Logger('info','Connessione avvenuta da :'+ str(Address))
        Client.send(WelcomeMsg.encode())
        Logger('debug',"Invio: " + WelcomeMsg)

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
                    Logger('debug','Ricevuto: ' + DataRecived)
                    Client.send((HeloMsg + Caller).encode())
                    Logger('debug','Invio: ' + HeloMsg + Caller)
                    DataRecived = ''
                elif bool(re.match('helo', DataRecived, re.I)):
                    try:
                        Caller = str(DataRecived.split(' ')[1])
                    except:
                        Caller = "Mister X\r\n"
                    Mail.RemoteSender = Caller
                    Logger('debug','Ricevuto: ' + DataRecived)
                    Client.send((HeloMsg + Caller).encode())
                    Logger('debug','Invio: ' + HeloMsg + Caller)
                    DataRecived = ''
                elif bool(re.match('mail from:', DataRecived, re.I)):
                    Logger('debug','Ricevuto: ' + DataRecived)
                    AddressMail = re.findall(r'<(.*?)>', DataRecived, re.DOTALL)[0]
                    Logger('debug',AddressMail)
                    Mail.AddMailFrom(str(AddressMail))
                    Client.send(MailFromMsg.encode())
                    Logger('debug','Invio: ' + MailFromMsg)
                    DataRecived = ''
                elif bool(re.match('rcpt to:', DataRecived, re.I)):
                    Logger('debug','Ricevuto: ' + DataRecived)
                    AddressMail = re.findall(r'<(.*?)>', DataRecived, re.DOTALL)[0]
                    Logger('debug',AddressMail)
                    Mail.AddRcptTo(str(AddressMail))
                    Client.send(RcptToMsg.encode())
                    Logger('debug','Inivo: ' + RcptToMsg)
                    DataRecived = ''
                elif bool(re.match('data', DataRecived, re.I)):
                    Logger('debug','Ricevuto: ' + DataRecived)
                    Client.send(DataMsg.encode())
                    Logger('debug','Invio: ' + DataMsg)
                    RealMail = ''
                    while not RealMail.endswith('\r\n.\r\n'):
                        DataRM = Client.recv(1024)
                        RealMail += DataRM.decode('utf-8')
                    Mail.MailObject = RealMail
                    Logger('debug','La mail ricevuta e:\r\n' + RealMail)
                    DBCursor = DataBaseConnection.cursor()
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
                    Logger('info',"Mail commitata nel db con ID: "+MailID)
                    DataRecived = ''
                    Mail.CleanData()

                elif bool(re.match('quit', DataRecived, re.I)):
                    Logger('debug','Ricevuto: ' + DataRecived)
                    Client.send(QuitMsg.encode())
                    Logger('debug','Inivo: ' + QuitMsg)
                    DataRecived = ''
                    Client.close()
                    ClientConnected = False

                else:
                    ErrorCount += 1
                    Logger('debug',"Error nr:"+str(ErrorCount))
                    Logger('info','Non ho codificato questo comando: ' + DataRecived)
                    DataRecived = ''

            Logger('debug',Mail.__dict__)


def ServerStop(message, code):
    #Server.close()
    Logger('info',"Chiudo il socket del server")
    Logger('debug',message)
    #Server.close()

#def MailReciver(ServerSocket, Mail, DataBaseConnection,Client,Address) :
#def MailReciver(ServerSocket, Mail, DataBaseConnection) :









