import socketio
import logging
import subprocess


logging.basicConfig(level=logging.INFO,
                    filename='server_connection.log',
                    filemode='a',  
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger('SocketIOClient')

sio = socketio.Client()

@sio.event
def connect():
    logger.info("Connected to the server.")
    sio.emit('identifyPi')  
    logger.info("Identified as Raspberry Pi to the server.")

@sio.event
def connect_error(data):
    logger.info(f"Connection failed: {data}")

@sio.event
def disconnect():
    logger.info("Disconnected from the server.")

@sio.event
def pumpControl(data):
    player_answer = data['playerAnswer'] 
    is_answer_correct = data['isAnswerCorrect']
    logger.info(f"Received pumpControl with playerAnswer: {player_answer} and is_answer_correct: {is_answer_correct}")

    pumpAnswerPath = '/home/sumit/sumit-pi/pumpAnswer.py'
    
    try:
        subprocess.run(['python3', pumpAnswerPath, player_answer, str(is_answer_correct)], check=True)
        logger.info(f"Successfully ran pumpAnswer with player_answer: {player_answer} and is_answer_correct: {is_answer_correct}")
    except subprocess.CalledProcessError as error:
        logger.error(f"Error running pumpAnswer.py: {error}")
    
    sio.emit('continueProcessing', {'status': 'ready'})
    logger.info("Sent continuation signal to the server.")

def main():
    try:
        sio.connect('https://sumit-back.onrender.com')
        logger.info("Attempting to connect to the server...")
        sio.wait()
    except Exception as exception:
        logger.error(f"An error occurred: {exception}")

if __name__ == '__main__':
    main()
