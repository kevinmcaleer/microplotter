class GCodeInterpreter:
    def __init__(self, motor_x, motor_y, motor_z):
        self.motor_x = motor_x
        self.motor_y = motor_y
        self.motor_z = motor_z
        self.position = {'X': 0, 'Y': 0, 'Z': 0}

    def parse_line(self, line):
        line = line.strip().upper()
        if not line or not line.startswith(('G0', 'G1')):
            return  # Ignore unsupported commands

        parts = line.split()
        cmd = parts[0]
        target = self.position.copy()

        for part in parts[1:]:
            axis = part[0]
            if axis in 'XYZ':
                try:
                    target[axis] = int(float(part[1:]))  # Convert to int steps
                except ValueError:
                    continue

        dx = target['X'] - self.position['X']
        dy = target['Y'] - self.position['Y']
        dz = target['Z'] - self.position['Z']

        # Perform movement
        if dx:
            self.motor_x.move(abs(dx), direction=1 if dx > 0 else -1)
        if dy:
            self.motor_y.move(abs(dy), direction=1 if dy > 0 else -1)
        if dz:
            self.motor_z.move(abs(dz), direction=1 if dz > 0 else -1)

        # Update current position
        self.position.update(target)
