import time
import os

def set_led_status(led_index, state):
    # led_index: 0 for green (activity), 1 for red (power)
    # state: "1" to turn on, "0" to turn off
    brightness_path = f"/sys/class/leds/{"PWR" if led_index else "ACT"}/brightness"
    # Ensure trigger is set to none first to allow manual control
    trigger_path = f"/sys/class/leds/{"PWR" if led_index else "ACT"}/trigger"
    
    os.system(f"sudo bash -c 'echo none > {trigger_path}'")
    os.system(f"sudo bash -c 'echo {state} > {brightness_path}'")

def reset_leds():
    trigger_path = f"/sys/class/leds/{"PWR" if 1 else "ACT"}/trigger"
    os.system(f"sudo bash -c 'echo default-on > {trigger_path}'")
    trigger_path = f"/sys/class/leds/{"PWR" if 0 else "ACT"}/trigger"
    os.system(f"sudo bash -c 'echo mmc0 > {trigger_path}'")



if __name__ == "__main__":
    set_led_status(0, "0")
    set_led_status(1, "0")
    time.sleep(2)
    set_led_status(0, "1") # Turn green back on
    time.sleep(1)
    reset_leds()