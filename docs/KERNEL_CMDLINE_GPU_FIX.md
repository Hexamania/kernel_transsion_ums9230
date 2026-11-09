# Kernel Cmdline Parameters for GPU Fix
# Add to boot.img kernel cmdline (in bootimg.cfg or via mkbootimg --cmdline)

## Mali GPU Power Management Fixes
# Enable driver-controlled GPU core stack power (bypasses PDC - helps with NULL callback)
mali_kbase.corestack_driver_control=Y

# Disable GPU polling (prevents power cycling)
mali_kbase.gpu_pollingtime=0

# Optional: Adjust DVFS thresholds
mali_kbase.gpu_upthreshold=80
mali_kbase.gpu_downdifferential=10

## Alternative: Disable kbase runtime PM entirely (if above doesn't work)
# Requires kernel with CONFIG_MALI_KBASE_PM_DISABLE or similar

---

# How to Apply (since you can repack boot.img):

1. Extract boot.img
2. Unpack with unpack_bootimg / mkbootimg
3. Edit cmdline in bootimg.cfg or use:
   ```
   mkbootimg --kernel Image --ramdisk ramdisk.img --cmdline "$(cat original_cmdline) mali_kbase.corestack_driver_control=Y mali_kbase.gpu_pollingtime=0" -o new_boot.img
   ```
4. Flash new_boot.img

---

# Root Cause Analysis:

**Hardware:** Infinix X6525 (Spreadtrum UMS9230 / Unisoc T606) → Mali-G57 MC2 (Valhall architecture)

**Kernel Driver:** mali_kbase r40p0 (Midgard architecture, UK version 11.36)

**Userspace Driver:** libGLES_mali.so (Valhall - correct for hardware)

**Mismatch:** Midgard kernel driver (r40p0) doesn't support Valhall power management callbacks
- Missing `backend->callback_power_off_second_part` → NULL pointer
- Causes GPU power cycling every ~6-60 seconds
- Chrome GPU process times out waiting for GPU channel during power transition
- Triggers "FATAL: Timed out waiting for GPU channel" → system death cascade

**Proper Fix:** Use Valhall-compatible mali_kbase kernel driver (r41p0+)
- Requires kernel rebuild with CONFIG_MALI_MIDGARD=n CONFIG_MALI_BIFROST=n CONFIG_MALI_VALHALL=y
- Or backport Valhall driver to 5.4 kernel

**Workarounds (in order of effectiveness):**
1. Kernel cmdline: `mali_kbase.corestack_driver_control=Y mali_kbase.gpu_pollingtime=0` (bypasses PDC, disables polling)
2. Magisk module: fix_gpu_pm (applies sysfs settings at boot)
3. Disable Chrome GPU acceleration (not ideal): `chrome --disable-gpu` or WebView flags

---

# Current Status:

✅ Magisk module created: `F:\platform-tools\fix_gpu_pm\`
   - module.prop
   - service.sh (late_start service)

✅ Runtime test: `power_policy=always_on` + `governor=performance` + `power/control=on` reduced cycling frequency but didn't stop it (kbase internal PM still active)

✅ Kernel cmdline parameters documented above for permanent fix

---

# To Install Magisk Module:

1. Copy `fix_gpu_pm` folder to `/data/adb/modules/` on device
2. Reboot, or use Magisk app "Install from storage"
3. Verify in Magisk app → Modules

# To Verify Fix Works:

```bash
# Check GPU stops cycling
adb shell "sleep 120; dmesg -T | grep -iE 'gpu|mali' | tail -20"

# Should see NO "kbase_pm_gpu_poweroff_wait_wq:backend->callback_power_off_second_part is NULL"
# Should see NO "SPRDDEBUG gpu shader core power on polling SUCCESS"

# Test Chrome
adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main
# Should not crash with "Timed out waiting for GPU channel"
```