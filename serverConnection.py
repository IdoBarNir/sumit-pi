import socketio
import logging
import subprocess
import time
import sys

# Set up logging to print to the terminal
logger = logging.getLogger('SocketIOClient')
logger.setLevel(logging.INFO)

# Create a StreamHandler to output logs to stdout
handler = logging.StreamHandler(sys.stdout)

# Optional: set a formatter if you want to customize the log output format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# Initialize the Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    logger.info("Connected to the server.")

@sio.event
def connect_error(data):
    logger.info(f"Connection failed: {data}")

@sio.event
def disconnect():
    logger.info("Disconnected from the server.")

@sio.event
def pumpControl(data):
    answer = data['answer']
    logger.info(f"Received answer: {answer}")

    # Specify the path to the SumIt.py script
    path_to_sumit = '/home/sumit/SumIt.py'
    
    # Attempt to run SumIt.py with the received answer as an argument
    try:
        subprocess.run(['python3', path_to_sumit, answer], check=True)
        logger.info(f"Successfully ran SumIt.py with answer: {answer}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running SumIt.py: {e}")
    
    # Sleep for 10 seconds before sending the continuation signal
    logger.info("Sleeping for 10 seconds...")
    time.sleep(10)  # Sleep for 10 seconds to simulate delay or waiting for an operation to complete
    
    # Send a continuation signal back to the server
    sio.emit('continueProcessing', {'status': 'ready'})
    logger.info("Sent continuation signal to the server.")

def main():
    try:
        # Connect to the server
        sio.connect('https://sumit-back.onrender.com')
        logger.info("Attempting to connect to the server...")
        # Wait for events
        sio.wait()
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
