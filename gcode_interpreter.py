import sys
class GCodeInterpreter:
    def __init__(self, motor_x, motor_y, motor_z):
        self.motor_x = motor_x
        self.motor_y = motor_y
        self.motor_z = motor_z
        self.position = {'X': 0, 'Y': 0, 'Z': 0}
        self.steps_per_mm = 10
        self.relative_mode = True  # G91 by default

    def parse_line(self, line):
        line = line.strip().upper()
        if not line or not line.startswith(('G0', 'G1','G90','G91')):
            sys.stdout.write("[MSG]:Unsupported commands {}\r\n".format(line))
            return  # Ignore unsupported commands

        parts = line.split() # ['G0' ,'X1', 'Y2', 'Z3']
        cmd = parts[0] #G0
        target = self.position.copy()

        if line == 'G90':
            self.relative_mode = False
            sys.stdout.write("[MSG: Setting positioning mode to Absolute]\r\n")
           
            return
        elif line == 'G91':
            self.relative_mode = True
            sys.stdout.write("[MSG: Setting positioning mode to Relative]\r\n")
          
            return

        moved_axes = set() 
        for part in parts[1:]:
            axis = part[0]
            value_str = part[1:]
            if axis in 'XYZ':
                try:
                    value = float(value_str)
                    step_value = int(value * self.steps_per_mm) if axis in 'XY' else int(value)
                    if self.relative_mode:
                        target[axis] = self.position[axis] + step_value
                    else:
                        target[axis] = step_value
                    moved_axes.add(axis)
                except ValueError:
                    sys.stdout.write("[MSG]: Invalid value '{}'\r\n".format(value_str))
                    continue

        
        dx = target['X'] - self.position['X'] if 'X' in moved_axes else 0
        dy = target['Y'] - self.position['Y'] if 'Y' in moved_axes else 0
        dz = target['Z'] - self.position['Z'] if 'Z' in moved_axes else 0
#         print("Computed target:", target)
#         print("Position before move:", self.position)
#         print("dx:", dx, " dy:", dy)

#         print(f"dx:'{dx}', dy:'{dy}', dz:'{dz}'")
        sys.stdout.write("[MSG:X:{}, Y:{}, Z:{}]\r\n".format(dx, dy, dz))
        
        # Perform movement
        if dx:
            self.motor_x.move(abs(dx), direction=1 if dx > 0 else -1)
            sys.stdout.write("[MSG:Moving X:{}]\r\n".format(dx))
        if dy:
            self.motor_y.move(abs(dy), direction=1 if dy > 0 else -1)
            sys.stdout.write("[MSG:Moving Y:{}]\r\n".format(dy))
        if dz:
         
#             print(f"dz is a {type(dz)}, value is {dz}")
            sys.stdout.write("[MSG:Moving Pen, dz is {}]\r\n".format(dz))
            # move pen either up or down - Z1 is up, Z0 is down
            if dz == 1: # up
                sys.stdout.write("[MSG:Moving pen up]\r\n")
                self.motor_z.move(50,direction=-1) # pen up
            else: # down
                sys.stdout.write("[MSG:Moving pen down]\r\n")
                self.motor_z.move(50,direction=1) # pen down
                
#             print("done moving")
        
        # Update current position
        for axis in moved_axes:
            self.position[axis] = target[axis]
        
    def set_position(self, **kwargs): # x=1,y=2, z =3
        for axis in ('X', 'Y', 'Z'):
            if axis in kwargs:
                self.position[axis] = kwargs[axis]

    def jog(self, dx=0, dy=0, dz=0):
        if dx:
            self.motor_x.move(abs(dx), direction=1 if dx > 0 else -1)
        if dy:
            self.motor_y.move(abs(dy), direction=1 if dy > 0 else -1)
        if dz:
            self.motor_z.move(abs(dz), direction=1 if dz > 0 else -1)
        # Don't update position, jogs are temporary unless committed

