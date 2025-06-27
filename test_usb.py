# main.py – MicroPython GRBL emulator for UGS with robust reconnect handling

from time import sleep, ticks_ms, ticks_diff
from stepper import StepperMotor
from gcode_interpreter import GCodeInterpreter
import sys, os, select

# Disable MicroPython REPL on USB
os.dupterm(None, 0)

motor_y = StepperMotor(0, 1, 2, 3, endstop_pin=16, endstop_direction=1)
# motor_x.invert_direction=True # the microswitch is on the right hand side
motor_x = StepperMotor(4, 5, 6, 7, endstop_pin=15, endstop_direction=-1)
motor_z = StepperMotor(8, 9, 10, 11)


gcode   = GCodeInterpreter(motor_x, motor_y, motor_z)
STEPS_PER_MM = 11 # 1000 steps = 9cm its about 11mm per step
gcode.steps_per_mm = STEPS_PER_MM

# --- At the top of your file, define settings with descriptions ---
grbl_settings = {
    0:  (10,   "Step pulse, usec"),
    1:  (25,   "Step idle delay, msec"),
    2:  (0,    "Step port invert mask"),
    3:  (0,    "Dir port invert mask"),
    4:  (0,    "Step enable invert, bool"),
    5:  (0,    "Limit pins invert, bool"),
    6:  (0,    "Probe pin invert, bool"),
    10: (3,    "Status report mask"),
    11: (0.010,"Junction deviation, mm"),
    12: (0.002,"Arc tolerance, mm"),
    13: (0,    "Report in inches, bool"),
    20: (0,    "Soft limits enable, bool"),
    21: (0,    "Hard limits enable, bool"),
    22: (0,    "Homing cycle enable, bool"),
    23: (0,    "Homing dir invert mask"),
    24: (25.0, "Homing feed, mm/min"),
    25: (500.0,"Homing seek, mm/min"),
    26: (250,  "Homing debounce, msec"),
    27: (1.000,"Homing pull-off, mm"),
    30: (1000, "Max spindle speed, RPM"),
    31: (0,    "Min spindle speed, RPM"),
    32: (1,    "Laser-mode enable, bool"),
}


# === State & timing constants ===
banner_sent        = False
question_counter   = 0
last_question_time = 0
last_status_time   = ticks_ms()

IDLE_RESET_MS      = 8000  # if no '?' for this long, treat as new session
REQ_INTERVAL_MS    = 1500  # max gap between two '?' for banner trigger
STATUS_INTERVAL_MS = 2000  # send idle status every 2s after banner

# === Poller for non-blocking stdin ===
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

# === Helpers ===
def send_status():
    pos = gcode.position
    sys.stdout.write(
        "<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
            pos['X'], pos['Y'], pos['Z']
        )
    )

def send_banner():
    """Send GRBL banner + a few idle status lines."""
    global banner_sent, last_status_time
    sys.stdout.write("Grbl 1.1f ['$' for help]\r\n")
    sys.stdout.write("<Idle|MPos:0.000,0.000,0.000|FS:0,0>\r\n")
    sys.stdout.write("[MSG:'$H'|'$X' to unlock]\r\n")
    for _ in range(3):
        send_status()
    banner_sent    = True
    last_status_time = ticks_ms()

# === Give the USB host a moment ===
sleep(1)

# === Main Loop ===
while True:
    try:
        now = ticks_ms()

        # If no '?' for a while, assume UGS reconnected → reset banner logic
#         if banner_sent and ticks_diff(now, last_question_time) > IDLE_RESET_MS:
#             banner_sent      = False
#             question_counter = 0

        # Periodic idle status after banner
        if banner_sent and ticks_diff(now, last_status_time) > STATUS_INTERVAL_MS:
            send_status()
            last_status_time = now

        # Check for incoming data
        if not poller.poll(0):
            continue

        line = sys.stdin.readline().strip("\r\n")
        if not line:
            continue

        # ——— Handle `?` probes ———
        if line == '?':
            # Count and time-stamp the `?`
            if ticks_diff(now, last_question_time) < REQ_INTERVAL_MS:
                question_counter += 1
            else:
                question_counter = 1
            last_question_time = now

            # On the second quick `?`, fire the banner if needed
            if not banner_sent and question_counter >= 2:
                send_banner()
                question_counter = 0
                continue  # skip status this round

            # After banner’s shown, always reply with status
            if banner_sent:
                send_status()
                last_status_time = now
                
            continue

        # ——— Soft reset (Ctrl-X) ———
        if line == '\x18':
            banner_sent      = False
            question_counter = 0
            continue

        # ——— Ensure banner before any '$' command ———
        if not banner_sent and line.startswith('$'):
            send_banner()

         # ——— GRBL-style commands ———
        if line == '$I':
            sys.stdout.write("[VER:MicroPythonGRBL:1.1]\r\n")
            sys.stdout.write("[OPT:MPY,USB,3AXIS]\r\n")
            sys.stdout.write("ok\r\n")

        elif line == '$X':
            sys.stdout.write("[MSG:Caution: Unlocked]\r\n")
            sys.stdout.write("ok\r\n")

        elif line == '$$':
            # Proper GRBL-style settings dump
            for key in sorted(grbl_settings):
                val, desc = grbl_settings[key]
                sys.stdout.write(f"${key}={val} ({desc})\r\n")
            sys.stdout.write("ok\r\n")

        elif line in ['$G','??$G','?$G']:
            # G90 means absolute positioning
            # G91 means relative positioning
            # G21 means?
            # G93 means?
            mode = "G91" if gcode.relative_mode else "G90"
            sys.stdout.write(f"[{mode} G21 G94]\r\n")
            sys.stdout.write("ok\r\n")
            
        elif line.startswith('G92'):
            # Set position
            new_pos = {}
            for tok in line.split()[1:]:
                axis, val = tok[0], float(tok[1:])
                if axis in 'XYZ':
                    new_pos[axis] = val
            gcode.set_position(**new_pos)
            sys.stdout.write("ok\r\n")

        elif line.startswith('$J='):
            # Jog (relative) only
            jog = line[3:].strip()
            if not jog.startswith("G91"):
                sys.stdout.write("error: Only G91 (relative) jogs supported\r\n")
            else:
                dx = dy = dz = 0
                for tok in jog.split():
                    if tok[0] == 'X':
                        dx = float(tok[1:]) * STEPS_PER_MM
                    elif tok[0] == 'Y':
                        dy = float(tok[1:]) * STEPS_PER_MM
                    elif tok[0] == 'Z':
                        dz = float(tok[1:]) * STEPS_PER_MM
                gcode.jog(dx, dy, dz)
                sys.stdout.write("ok\r\n")
        elif line in ['$H','$H']:
            sys.stdout.write("[MSG:Homing...]\r\n")
            # Move until endstop is hit
            while not motor_x.is_endstop_triggered():
                motor_x.move(1, direction=-1)  # move slowly in -X until stop
                sys.stdout.write("[MSG: Moving X]\r\n")
            while not motor_y.is_endstop_triggered():
                motor_y.move(1, direction=1)
                sys.stdout.write("[MSG: Moving Y]\r\n")
            motor_x.stop()
            motor_y.stop()
            gcode.set_position(X=0,Y=0)
            sys.stdout.write("ok\r\n")

        else:
            # All other G-code (motion)
            gcode.parse_line(line)
            sys.stdout.write("ok\r\n")

    except Exception as e:
        sys.stdout.write("error: {}\r\n".format(e))
