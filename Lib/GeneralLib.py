##########
# IMPORT #
##########
import logging

##############
# FUNCTIONS #
#############

def Logger (lvl,message):
    logging.basicConfig(
        filename='/var/log/objmail/ReceiverDaemon.log',
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
    )
    if lvl == 'debug' :
        logging.debug(message)
    elif lvl == 'info' :
        logging.info(message)
    elif lvl == 'error':
        logging.error(message)




########
# TEST #
#######
