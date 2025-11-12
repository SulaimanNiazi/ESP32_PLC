# ⚙️ ESP32_PLC  

![Python](https://img.shields.io/badge/MicroPython-1.20%2B-blue?logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/Board-ESP32--WROOM32-orange?logo=espressif)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

🧠 Turn your ESP32 into a tiny **Programmable Logic Controller (PLC)** powered by MicroPython.

---

## 🪄 Overview  

**ESP32_PLC** transforms your ESP32-WROOM-32 into a **fully programmable logic controller (PLC)**.  
You can control and interconnect GPIOs using **simple terminal commands** — define AND, OR, XOR, and NOT gates, or directly wire signals together in real-time.  

Once uploaded as `main.py`, the ESP32 automatically boots into PLC mode and starts executing logic cycles continuously, just like an industrial PLC.

---

## ✨ Features  

✅ Command-line interface (CLI) via UART or REPL  
✅ Real-time logic execution in a background thread  
✅ Supports logic gates:

- ➕ **OR** (`+`)
- ✖️ **AND** (`*`)
- ⛔ **NOT** (`!`)
- ⚡ **XOR** (`^`)
- ➡️ **One Way Wire (diode)** (`=`)

✅ Pin protection for flashing/memory lines  
✅ Dynamic reconfiguration without reboot  
✅ Built-in reset and diagnostics commands  

---

<details>
<summary>📋<b>Supported Commands</b></summary>

| Command | Description | Example |
|----------|-------------|----------|
| `pin` | Read digital input | `12` |
| `pin = value` | Set output pin (0, 1, or X for input) | `12 = 1` / `12 = x` |
| `pin = ! in` | NOT gate | `13 = ! 12` |
| `pin = in1 + in2` | OR gate | `15 = 12 + 13` |
| `pin = in1 * in2` | AND gate | `16 = 12 * 13` |
| `pin = in1 ^ in2` | XOR gate | `17 = 12 ^ 13` |
| `pin = ! in1 + in2` | NOR gate | `15 = ! 12 + 13` |
| `pin = ! in1 * in2` | NAND gate | `16 = ! 12 * 13` |
| `pin = ! in1 ^ in2` | XNOR gate | `17 = ! 12 ^ 13` |
| `gates ?` | List configured gates | `gates` |
| `reset` | Restart the ESP32 | `reset` |

💡 Add `?` at the end of any command for **debug mode** to show detailed error messages.
</details>

---

## 🧠 Example Session

```text
> 15 = 12 + 13
OK
> 14 = ! 12 + 13
OK
> 13 = 1
OK
> 15
OK
1
> GATES
OK
Pin(15) = Pin(12) + Pin(13)
Pin(14) = !(Pin(12) + Pin(13))
> 15 = x
OK
> 14 = x
OK
> gates
OK
NONE
> reset
OK
```

---

## 🛠️ Setup Instructions

### 1️⃣ Flash MicroPython

Use [esptool.py](https://docs.espressif.com/projects/esptool/en/latest/esp32/installation.html) to flash [MicroPython firmware](https://micropython.org/download/ESP32_GENERIC/) on your ESP32:

```bash
esptool -p COMx erase-flash
esptool -p COMx write-flash 0x1000 ESP32_GENERIC-v1.xx.x.bin
```

### 2️⃣ Upload the Script

Copy `main.py` (this script) to your ESP32 using [**Arduino Lab**](https://labs.arduino.cc/en/labs/micropython), **Thonny**, **ampy**, or **rshell**.

### 3️⃣ Run Automatically

The script will run on startup if you save it as `main.py`.
That means your PLC logic starts automatically when powered!

---

## 🚨 Pin Safety

The following pins are **protected** to prevent interference with flash memory or serial programming:

| Type         | Pins |
| ------------ | ---- |
| Flash/Debug  | 1, 3 |
| Flash Memory | 6-11 |

Any attempt to use these pins will result in an error.

Furthermore:

- Directly shorting the gates inputs and outputs or duplicating gates will result in error.
- Overwriting output pins will result in the deletion/replacement of gates.
