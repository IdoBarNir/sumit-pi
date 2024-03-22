import sys
import time
import threading
import gpio
from pygame import mixer

mixer.init()
start_music = mixer.Sound("start.mp3")
stop_music = mixer.Sound("stop.mp3")
pump_pin = 20
speaker_pin = 21
valves = {
    'A': {'in': 22, 'out': 25, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'B': {'in': 5, 'out': 16, 'in-duration': 60, "buffer":5, "out-duration": 60},
    'C': {'in': 6, 'out': 26, 'in-duration': 60, "buffer":5, "out-duration": 60},
}

def operate_valve(valve):
    start_music.play()
    gpio.On(valves[valve]['in'])
    print(f"Valve {valve}-In opened")
    
    time.sleep(valves[valve]['in-duration'])
    gpio.Off(valves[valve]['in'])
    print(f"Valve {valve}-In closed")

    time.sleep(valves[valve]['buffer'])
    start_music.stop()

    stop_music.play()
    gpio.On(valves[valve]['out'])
    print(f"Valve {valve}-Out opened")


    time.sleep(valves[valve]['out-duration'])
    stop_music.stop()
    print(f"Valve {valve}-Out closed")

def control_valves(player_answer):
    print("Starting valve operations...")

    threads = []
    for valve in player_answer:
        if valve in valves:
            thread = threading.Thread(target=operate_valve, args=(valve,))
            threads.append(thread)
            thread.start()
        else:
            print(f"Invalid valve code: {valve}")
    
    for thread in threads:
        thread.join()
    
    print("Completed all valve operations.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        sys.exit(1)

    player_answer = sys.argv[1].upper()
    is_answer_correct = sys.argv[2]  # Currently not used, can be used to play specific sound based on answer correctness.

    gpio.On(speaker_pin)
    gpio.On(pump_pin)

    control_valves(player_answer)

    gpio.Off(pump_pin)
    gpio.Off(speaker_pin)
