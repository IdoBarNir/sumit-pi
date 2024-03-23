import sys
import gpio
import time
import threading
import logging

logging.basicConfig(level=logging.INFO,
                    filename='pump_answer.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


pump_pin = 20
speaker_pin = 21
valves = {
    'A': {'in': 22, 'out': 25, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'B': {'in': 5, 'out': 16, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'C': {'in': 6, 'out': 26, 'in-duration': 60, "buffer":5, "out-duration": 60},
}
GPIOpins = [23,17,24,27,25,22,16,5,6,26,21,20]
gpio.Init(GPIOpins)

def operate_valve(valve, is_answer_correct):
    gpio.On(valves[valve]['in'])
    logger.info(f"Valve {valve}-In opened")
    
    time.sleep(valves[valve]['in-duration'])
    gpio.Off(valves[valve]['in'])
    logger.info(f"Valve {valve}-In closed")

    if is_answer_correct == 'True':
        logger.info("Playing win music")
    else:
        logger.info("Playing lose music")
 
    time.sleep(valves[valve]['buffer'])

    gpio.On(valves[valve]['out'])
    logger.info(f"Valve {valve}-Out opened")

    time.sleep(valves[valve]['out-duration'])
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
    sys.exit(0)

