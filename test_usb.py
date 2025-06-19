# main.py - MicroPython GRBL-compatible interpreter for UGS

from time import sleep, ticks_ms, ticks_diff
from stepper import StepperMotor
from gcode_interpreter import GCodeInterpreter
import sys
import os
import select

# Disable REPL on USB to avoid collisions.
# This is crucial for dedicated serial communication with UGS.
os.dupterm(None, 0)

# Initialize stepper motors with their respective pins.
# (Ensure StepperMotor and GCodeInterpreter classes are defined in their respective modules:
#  stepper.py and gcode_interpreter.py, and are accessible).
motor_x = StepperMotor(14, 15, 18, 23)
motor_y = StepperMotor(2, 3, 4, 5)
motor_z = StepperMotor(6, 7, 8, 9)

# Initialize the GCodeInterpreter, passing the motor instances.
gcode = GCodeInterpreter(motor_x, motor_y, motor_z)

# Define steps per millimeter for accurate movement calculations.
# This should match your plotter's physical configuration.
STEPS_PER_MM = 10

# Global flags and timing variables for managing GRBL state and communication.
banner_sent = False
# Removed question_counter and last_question_time. The revised logic
# ensures banner is sent proactively or on explicit reset/query,
# rather than relying on a counter for '?' commands.
last_status = ticks_ms() # Timestamp for the last status report sent.

# Set up polling for non-blocking input from stdin (USB serial).
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

def send_banner():
    """
    Sends the GRBL startup banner and initial status messages.
    This mimics GRBL's power-on behavior, crucial for UGS handshake.
    """
    global banner_sent, last_status
    # Prevent sending the banner multiple times unless explicitly reset.
    if banner_sent:
        return

    # 1. Main GRBL version banner.
    sys.stdout.write("Grbl 1.1f ['$' for help]\r\n")

    # 2. Informational message (e.g., how to unlock/home).
    # This typically comes after the main banner.
    sys.stdout.write("[MSG:'$H'|'$X' to unlock]\r\n")

    # 3. Send a few initial status reports. UGS often expects several
    #    to ensure a stable connection and initial state.
    for _ in range(3):
        pos = gcode.position # Get current machine position from the interpreter.
        sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
            pos['X'], pos['Y'], pos['Z'] # Format positions to 3 decimal places.
        ))
        sleep(0.01) # Small delay to ensure messages are sent separately if buffering is aggressive.

    # Mark banner as sent and update last status time.
    banner_sent = True
    last_status = ticks_ms()

# --- Initial Setup on Boot ---
# Wait a moment for the USB serial connection to stabilize.
sleep(1)
# Immediately send the GRBL banner on startup. This is often the fix for UGS "connecting" issues,
# as UGS expects this response very quickly after establishing the serial link.
send_banner()

# --- Main Loop for GRBL Communication ---
while True:
    try:
        now = ticks_ms()

        # Send periodic status reports if the banner has been sent.
        # This keeps UGS updated on the plotter's state (e.g., Idle, Run, Hold).
        if banner_sent and ticks_diff(now, last_status) > 2000: # Send every 2 seconds.
            pos = gcode.position
            sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                pos['X'], pos['Y'], pos['Z']
            ))
            last_status = now # Update timestamp of last status report.

        # Check for incoming data on stdin (USB serial) without blocking.
        if not poller.poll(0):
            continue # No new data, continue to next loop iteration (for periodic status).

        # Read the incoming line, stripping newline/carriage return characters.
        line = sys.stdin.readline().strip("\r\n")
        if not line:
            continue # Empty line received, ignore.

        # --- Handle Incoming Commands ---

        # 1. Status Report Request ('?').
        if line == '?':
            # Always respond to '?' with a current status report.
            if banner_sent: # Only if connection is established.
                pos = gcode.position
                sys.stdout.write("<Idle|MPos:{:.3f},{:.3f},{:.3f}|FS:0,0>\r\n".format(
                    pos['X'], pos['Y'], pos['Z']
                ))
                last_status = now
            else:
                # Fallback: if '?' somehow arrives before banner, send the banner.
                send_banner()
            continue # Processed '?', move to next loop iteration.

        # 2. Soft Reset (Ctrl-X, ASCII 24).
        # This command should reset the GRBL state and re-send the banner.
        if line == '\x18': # Ctrl-X character.
            banner_sent = False # Flag to allow the banner to be re-sent.
            gcode.reset_state() # <<< IMPORTANT: YOU NEED TO IMPLEMENT THIS IN GCodeInterpreter!
                                #     This method should reset current position, modal states (G90/G91), etc.
            send_banner() # Re-send the full banner immediately after a soft reset.
            continue

        # 3. Query Build Info ('$I').
        # Responds with build information and an 'ok'. Also re-sends the banner in real GRBL.
        elif line == '$I':
            banner_sent = False # Ensure full banner is resent as part of $I response.
            send_banner()
            sys.stdout.write("[VER:MicroPythonGRBL:1.1]\r\n") # Custom version string.
            sys.stdout.write("[OPT:MPY,USB,3AXIS]\r\n") # Custom options string.
            sys.stdout.write("ok\r\n") # Acknowledge the command.
            continue

        # 4. Unlock ($X).
        elif line == '$X':
            sys.stdout.write("ok\r\n") # Acknowledge unlock command.

        # 5. View GRBL Settings ($$).
        elif line == '$$':
            sys.stdout.write("$$=not_implemented\r\n") # Placeholder for settings.
            sys.stdout.write("ok\r\n")

        # 6. View G-code Parser State ($G).
        elif line == '$G':
            # This should reflect actual current modal states if implemented fully.
            sys.stdout.write("[G91 G21 G94]\r\n")
            sys.stdout.write("ok\r\n")

        # 7. Set Position Offset (G92).
        elif line.startswith('G92'):
            new_pos = {}
            for token in line.split()[1:]: # Parse X, Y, Z components.
                axis = token[0]
                value = float(token[1:])
                if axis in 'XYZ':
                    new_pos[axis] = value
            gcode.set_position(**new_pos) # Update interpreter's position.
            sys.stdout.write("ok\r\n")

        # 8. Jog Command ($J=...).
        elif line.startswith('$J='):
            jog_cmd = line[3:].strip() # Extract the jog G-code.
            if not jog_cmd.startswith("G91"):
                sys.stdout.write("error: Only G91 (relative) jogs supported\r\n")
            else:
                dx = dy = dz = 0
                for token in jog_cmd.split():
                    if token.startswith('X'):
                        dx = float(token[1:]) * STEPS_PER_MM
                    elif token.startswith('Y'):
                        dy = float(token[1:]) * STEPS_PER_MM
                    elif token.startswith('Z'):
                        dz = float(token[1:]) * STEPS_PER_MM
                gcode.jog(dx, dy, dz) # Execute jog movement.
                sys.stdout.write("ok\r\n")

        # 9. General G-code Commands.
        else:
            gcode.parse_line(line) # Pass the line to the G-code interpreter.
            sys.stdout.write("ok\r\n") # Acknowledge successful processing.

    except Exception as e:
        # Catch any unexpected errors and report them back to UGS.
        sys.stdout.write("error: {}\r\n".format(str(e)))
