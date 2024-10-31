// Define the pin for the LED
const int LED { 17 };

// Define status codes for success and error
const char S_OK { 0xaa };
const char S_ERR { 0xff };

// This function is called when a byte is received over serial
void on_receive(void* event_handler_arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    // Read one byte from the serial buffer
    char state { USBSerial.read() };

    // Check if the byte represents a valid LED state
    if (!(state == LOW || state == HIGH)) {
        // If invalid, send error response and exit
        USBSerial.write(S_ERR);
        return;
    }

    // If valid, set the LED state and send success response
    digitalWrite(LED, state);
    USBSerial.write(S_OK);
}

void setup() {
    // Set the LED pin as output
    pinMode(LED, OUTPUT);

    // Register on_receive as callback for the RX event
    USBSerial.onEvent(ARDUINO_HW_CDC_RX_EVENT, on_receive);

    // Start serial communication at 9600 baud
    USBSerial.begin(9600);
}

void loop() {
    // Nothing needed here; interrupt-driven system
}
