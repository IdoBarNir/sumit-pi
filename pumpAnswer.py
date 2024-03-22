import sys
import time
import threading
import logging
import gpio
from pygame import mixer

logging.basicConfig(level=logging.INFO,
                    filename='pump_answer.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

mixer.init()
start_music = mixer.Sound("start.mp3")
stop_music = mixer.Sound("stop.mp3")
win_music = mixer.Sound("dance.mp3")  
lose_music = mixer.Sound("dance.mp3")  

pump_pin = 20
speaker_pin = 21
valves = {
    'A': {'in': 22, 'out': 25, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'B': {'in': 5, 'out': 16, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'C': {'in': 6, 'out': 26, 'in-duration': 60, "buffer":5, "out-duration": 60},
}

def operate_valve(valve, is_answer_correct):
    start_music.play()
    gpio.On(valves[valve]['in'])
    logger.info(f"Valve {valve}-In opened")
    
    time.sleep(valves[valve]['in-duration'])
    gpio.Off(valves[valve]['in'])
    logger.info(f"Valve {valve}-In closed")

    start_music.stop()
    if is_answer_correct == 'True':
        win_music.play()
    else:
        lose_music.play()
    
    time.sleep(valves[valve]['buffer'])

    stop_music.play()
    gpio.On(valves[valve]['out'])
    logger.info(f"Valve {valve}-Out opened")

    time.sleep(valves[valve]['out-duration'])
    stop_music.stop()
    logger.info(f"Valve {valve}-Out closed")

def control_valves(player_answer, is_answer_correct):
    logger.info("Starting valve operations...")

    threads = []
    for valve in player_answer:
        if valve in valves:
            thread = threading.Thread(target=operate_valve, args=(valve, is_answer_correct))
            threads.append(thread)
            thread.start()
        else:
            logger.warning(f"Invalid valve code: {valve}")
    
    for thread in threads:
        thread.join()
    
    logger.info("Completed all valve operations.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("Incorrect number of arguments.")
        sys.exit(1)

    player_answer = sys.argv[1].upper()
    is_answer_correct = sys.argv[2]

    gpio.On(speaker_pin)
    gpio.On(pump_pin)

    control_valves(player_answer, is_answer_correct)

    gpio.Off(pump_pin)
    gpio.Off(speaker_pin)
