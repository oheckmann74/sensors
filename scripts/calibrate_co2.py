import board
import busio
import adafruit_scd30
# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the interface to the SCD30 sensor (CO2, Temperature, Humidity)
scd = adafruit_scd30.SCD30(i2c)

scd.self_calibration_enabled = True
scd.self_calibration_enabled = False
scd.altitude = 48

