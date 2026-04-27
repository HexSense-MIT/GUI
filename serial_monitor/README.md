# ESP32 Web Serial Monitor

A modern, feature-rich web-based serial monitor for ESP32 and other microcontrollers using the Web Serial API.

## Features

### Core Functionality
- **Web Serial API Integration** - Connect directly to ESP32/Arduino via USB
- **Configurable Baud Rates** - Support for 9600 to 921600 baud
- **Real-time Data Display** - Live serial data streaming
- **Send Data** - Send commands to your device with configurable line endings
- **HEX Mode** - View data in hexadecimal format

### Display Features
- **Customizable Themes** - Dark, Light, and Terminal presets
- **Color Coding** - Automatic detection of error, warning, info, and debug messages
- **Custom Colors** - Full color customization for all message types
- **Adjustable Font Size** - 10-24px range
- **Line Height Control** - Customize spacing between lines
- **Timestamps** - Optional millisecond-precision timestamps
- **Auto-scroll** - Automatically scroll to latest output
- **Data Filtering** - Filter output in real-time
- **Line Limiting** - Set max lines to prevent memory issues

### Statistics
- **RX/TX Byte Counter** - Track data transmitted and received
- **Line Counter** - Track number of lines displayed

## Browser Support

This application requires the **Web Serial API**, which is supported in:
- Chrome 89+
- Edge 89+
- Opera 76+

**Note:** Firefox and Safari do not currently support the Web Serial API.

## How to Use

### 1. Open the Application
Simply open `index.html` in a supported browser:
```bash
# You can use Python's built-in server
python3 -m http.server 8000

# Then open: http://localhost:8000
```

Or double-click `index.html` to open directly in your browser.

### 2. Connect to Your Device
1. Click the **Connect** button
2. Select your ESP32/Arduino from the port selection dialog
3. The monitor will start displaying data immediately

### 3. Customize Your Display
Click the **Settings** button to access:
- Theme presets (Dark/Light/Terminal)
- Font size and line height
- Custom colors for each message type
- Background color
- Maximum line limit

### 4. Send Data
Type your command in the input field at the bottom and:
- Press **Enter** or click **Send**
- Select line ending format (None, \n, \r, or \r\n)

### 5. Filter Output
Use the **Filter** input to show only lines containing specific text.

## Keyboard Shortcuts
- **Enter** - Send data when input field is focused

## Automatic Log Level Detection

The monitor automatically detects and color-codes messages:
- **Error** - Lines containing: "error", "err:", "failed"
- **Warning** - Lines containing: "warning", "warn:"
- **Info** - Lines containing: "info:", "[i]"
- **Debug** - Lines containing: "debug", "dbg:"

## Settings Persistence

All your customization settings are automatically saved to browser localStorage:
- Theme and colors
- Font size and line height
- Baud rate
- Auto-scroll preference
- Timestamp preference
- Line ending preference

## Example ESP32 Code

```cpp
void setup() {
  Serial.begin(115200);
  Serial.println("INFO: ESP32 Serial Monitor Test");
}

void loop() {
  Serial.println("Debug: Loop iteration");
  Serial.println("Warning: Temperature high");
  Serial.println("Error: Sensor not found");
  delay(1000);
}
```

## Troubleshooting

### "Web Serial API is not supported"
- Use Chrome, Edge, or Opera browser
- Ensure you're using HTTPS or localhost

### Can't see my device
- Make sure the device is plugged in
- Check that drivers are installed (CH340, CP2102, etc.)
- Try a different USB cable or port

### Data looks garbled
- Check the baud rate matches your device
- Verify the device is actually sending data

### Connection drops
- Check USB cable quality
- Avoid USB hubs if possible
- Check device power supply

## File Structure

```
serial_monitor/
├── index.html           # Main HTML structure
├── serial-monitor.js    # Application logic
└── README.md           # This file
```

## License

Free to use for personal and commercial projects.
