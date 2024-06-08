import serial
import serial.tools.list_ports
import time

def find_cash_drawer():
    # Iterate over all available serial ports
    for port in serial.tools.list_ports.comports():
        # Check if the port description contains the desired string
        if "Prolific USB-to-Serial Comm Port" in port.description:
            try:
                # Open serial port
                ser = serial.Serial(port.device, 9600, timeout=1)
                
                # The command to open the cash drawer.
                # This command may vary depending on the manufacturer.
                command = b'\x1B\x70\x00\x19\xFA'
                
                # Send the command to the cash drawer
                ser.write(command)
                
                # Read response or wait to ensure command execution
                response = ser.read(2)  # Adjust read size and timeout as needed
                
                # Close the serial port
                ser.close()
                
                print(f"Cash drawer opened successfully on port {port.device}")
                return port.device
            
            except Exception as e:
                print(f"Error on port {port.device}: {e}")
    
    print("Could not find the cash drawer.")
    return None

def open_cash_drawer(port):
    try:
        # Open serial port
        ser = serial.Serial(port, 9600, timeout=1)
        
        # The command to open the cash drawer.
        # This command may vary depending on the manufacturer.
        # The common command is a series of bytes such as ESC p (0x1B 0x70).
        command = b'\x1B\x70\x00\x19\xFA'
        
        # Send the command to the cash drawer
        ser.write(command)
        
        # Close the serial port
        ser.close()
        
        print("Cash drawer opened successfully.")
    except Exception as e:
        print(f"Error opening cash drawer: {e}")

if __name__ == "__main__":
    start_time = time.time()
    
    port = find_cash_drawer()
    if port:
        open_cash_drawer(port)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"Total execution time: {elapsed_time:.2f} seconds")
