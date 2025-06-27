G21         ; Set units to millimeters
G90         ; Use absolute positioning
$H          ; Home
G1 X0 Y0 F500 ; Move to starting corner
G1 Z-1 F300  ; Lower the tool to the surface

; Draw the square
G1 X10 Y0 F500  ; Move to right corner
G1 X10 Y10      ; Move to top-right corner
G1 X0 Y10       ; Move to top-left corner
G1 X0 Y0        ; Move back to origin

G1 Z1 F300      ; Lift the tool up again
