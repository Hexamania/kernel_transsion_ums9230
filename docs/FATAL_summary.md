# FATAL Entries from log.txt (Sorted)

Total FATAL entries found: **14**

---

## 1. GPU Channel Timeout (Chromium) - 4 occurrences

### Timestamp: 11-08 19:01:20.494
**PID:** 9931 (crash_dump64) → **Process:** com.android.chrome (PID 6952)
**Error:** `[FATAL:content/browser/gpu/browser_gpu_channel_host_factory.cc:49] Timed out waiting for GPU channel.`
**Signal:** SIGTRAP (5), TRAP_BRKPT
**Backtrace:** libmonochrome_64.so → libutils.so (Looper::pollOnce) → libart.so

### Timestamp: 11-08 19:04:10.161
**PID:** 15730 (crash_dump64) → **Process:** com.android.chrome
**Error:** `[FATAL:content/browser/gpu/browser_gpu_channel_host_factory.cc:49] Timed out waiting for GPU channel.`

### Timestamp: 11-08 19:07:26.827
**PID:** 20064 (chromium) → **Process:** chromium
**Error:** `[FATAL:content/browser/gpu/browser_gpu_channel_host_factory.cc:49] Timed out waiting for GPU channel.`

### Timestamp: 11-08 19:07:28.525
**PID:** 21511 (crash_dump64) → **Process:** chromium
**Error:** `[FATAL:content/browser/gpu/browser_gpu_channel_host_factory.cc:49] Timed out waiting for GPU channel.`

---

## 2. DeadSystemException (System Death) - 4 occurrences

### Timestamp: 11-08 19:02:20.273
**PID:** 1632 → **Process:** com.android.phone
**Error:** `DeadSystemException: The system died; earlier logs will point to the root cause`

### Timestamp: 11-08 19:02:20.286
**PID:** 3951/3982 → **Process:** com.skms.android.agent (IntentService[eSEFraService])
**Error:** `DeadSystemException: The system died; earlier logs will point to the root cause`

### Timestamp: 11-08 19:05:22.725
**PID:** 11337/11415 → **Process:** wmshell.main
**Error:** `FATAL EXCEPTION: wmshell.main`

### Timestamp: 11-08 19:05:22.911
**PID:** 11337 → **Process:** main
**Error:** `FATAL EXCEPTION: main`

### Timestamp: 11-08 19:05:23.061
**PID:** 11785/16271 → **Process:** IntentService[DropBoxEntryAddedChimeraService]
**Error:** `FATAL EXCEPTION: IntentService[DropBoxEntryAddedChimeraService]`

---

## 3. Audio System Crash - 1 occurrence

### Timestamp: 11-08 19:02:47.935
**PID:** 3043/3301 → **Process:** audio-in
**Error:** `FATAL EXCEPTION: audio-in`

---

## 4. DeviceDoctor / Highpool Crashes - 3 occurrences

### Timestamp: 11-08 19:08:22.064
**PID:** 17489/18504 → **Process:** DeviceDoctorHandler (highpool[9])
**Error:** `FATAL EXCEPTION: highpool[9]`

### Timestamp: 11-08 19:08:22.145
**PID:** 17015 → **Process:** main
**Error:** `FATAL EXCEPTION: main`

### Timestamp: 11-08 19:08:22.153
**PID:** 17113/17425 → **Process:** WifiPickerTracker-WifiRepository
**Error:** `FATAL EXCEPTION: WifiPickerTracker-WifiRepository`

---

## 5. Other System Crashes - 2 occurrences

### Timestamp: 11-08 19:08:22.604
**PID:** 20001 → **Process:** main
**Error:** `FATAL EXCEPTION: main`

### Timestamp: 11-08 19:08:22.627
**PID:** 19195/19239 → **Process:** IntentService[eSEFraService]
**Error:** `FATAL EXCEPTION: IntentService[eSEFraService]`

---

## Root Cause Analysis

**Primary Issue (from memory files):** CM4 PMIC Watchdog Timeout (`sprd_pmic_wdt` module)
- Causes unclean shutdown during reboot
- Corrupts f2fs + FBE encryption on /data (mmcblk0p73)
- Recovery fails to mount /data → requires `fastboot -w`

**Secondary Issues (from log):**
1. **GPU Channel Timeout** - Chromium GPU process failing to establish channel (driver/HAL mismatch)
2. **Samsung HALs Missing** - `vendor.samsung.hardware.security.sem.ISehSem`, `vendor.samsung.hardware.radio.channel.ISehRadioChannel` not found (expected for cross-port)
3. **System Death Cascade** - DeadSystemException propagates to all processes when system_server dies

---

## Fix Applied

**Magisk Module Created:** `F:\platform-tools\disable_pmic_wdt\`
- **module.prop** - Module metadata
- **service.sh** - Late_start service that runs `rmmod sprd_pmic_wdt` after boot completes

**Alternative Fix (Kernel Cmdline):**
```
module_blacklist=sprd_pmic_wdt
```

This prevents the PMIC watchdog module from loading. The FIQ watchdog (`sprd_wdt_fiq`) still provides watchdog functionality.