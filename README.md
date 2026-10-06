# Kamoer X1 Pro v2 — Home Assistant (Bluetooth)

A Home Assistant custom integration that controls a **Kamoer X1 Pro V2** over **Bluetooth Low Energy**: set a volume in mL and start/stop a dose from HA. No cloud, no MQTT, no proxy, no phone app needed.

> ⚠️ **Experimental.** The protocol was reverse-engineered from one phone capture of the app's flow-calibration screen. The connection handshake and the "set volume" write are verified against that capture. **The dose start/stop commands are not** (see [Status](#status)). Test with the pump's output in a measuring cup, not the tank. Interoperability work on hardware you own; no warranty.

## Install
1. Install [HACS](https://hacs.xyz) if you haven't already.
2. HACS → ⋮ → **Custom repositories** → add `https://github.com/kairsato/kamoer-x1-pro-v2-ble-hacs` (category: Integration).
3. Find **Kamoer X1 Pro V2 (Bluetooth)** in HACS and **Download** it.
4. Restart Home Assistant.
5. Make sure the pump is visible over Bluetooth and Home Assistant has a Bluetooth adapter (or an [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy.html)) in range. You can check with your phone: the pump should show up as `KAMOER_*`. **Close the Kamoer phone app first** (force-stop it): the pump allows only one Bluetooth connection.

The pump should then appear under **Settings → Devices & services → Discovered**.

## Entities
| Entity | What it does |
|---|---|
| `number` Dose volume (mL) | The amount to dose, 0–5000 mL. Only stored; changing it never moves the pump. |
| `button` Start dose | Connects, sends the volume, then starts. |
| `button` Stop | Sends the stop command. |
| `button` Refresh status *(diagnostic)* | Reads the pump's status. |
| `sensor` Last reply / Last error *(diagnostic)* | The pump's last notification (raw hex, not decoded yet) and any connection error. |

The integration connects only when an action runs, then disconnects, so the phone app can still connect in between.

## Status
**Verified** against the capture (`tests/test_protocol.py` rebuilds the captured frames byte for byte, and the startup sequence plus a set-volume write were confirmed on a real pump with nRF Connect):
- GATT layout and framing (below); no pairing, bonding or encryption needed.
- The three startup frames the pump needs before it accepts anything else.
- The "set volume" write.

**Unverified:**
- **Start** reuses the `0013` frame the app sent on every calibration run. It's believed to be "run" but was never seen as a normal dose.
- **Stop** is a guess (the same frame with the enable word cleared). Don't rely on it as a safety stop; cut power or use the app.
- Whether the volume unit is mL for normal doses, and whether the pump auto-stops at the target.
- The pump's replies and status fields aren't decoded, so there's no progress sensor yet.

## Protocol notes
- Service `0xFFFF`; write characteristic `0xFF01` (Write Request); notify characteristic `0xFF02` (enable by writing `0100` to its CCCD). MTU 517.
- Write frame: `4d 00 <seq> <len> <counter u16le> <body>`. Reply frame: `4d 04 <seq> <len> <counter u16le> <body>`. `len` counts the bytes after it; `seq` starts at 0 on each connection and increments per write.
- **Send these first, waiting for the reply to each**, or the pump rejects later frames (it answers `49 04 …`):
  ```
  4d000009390200010001000100
  4d0001083a02000000000002
  4d00020a3b020002000100040100
  ```
- Set volume (seq 3 shown; the volume is a big-endian float32):
  ```
  4d0003123c02000a0001000300013f80000000000000   # 1.0
  4d0004123d02000a0001000300014000000000000000   # 2.0
  ```
