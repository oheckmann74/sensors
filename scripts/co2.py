import board
import busio
import adafruit_scd30

i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)


if scd.data_available:
    print(f'CO2: {scd.CO2:.0f} PPM')
    print(f'Humidity: {scd.relative_humidity:.1f}%rH')
    print(f'Temperature: {scd.temperature} ˚C / {scd.temperature * 9/5+32}˚F')
else:
    print("No data available - try again later...")