# Mali CSF Driver Build - Quick Reference

## The Problem
- **Hardware**: Mali-G57 MC2 (Valhall architecture)
- **Current Kernel Driver**: Midgard r40p0 (no CSF/Valhall support)
- **Result**: GPU power cycling → Chrome crashes → black screen

## The Fix
Build **mali_kbase** kernel module with **CSF (Command Stream Frontend) support** enabled:
- `CONFIG_MALI_MIDGARD=m`
- `CONFIG_MALI_CSF_SUPPORT=y` ← **THIS ENABLES VALHALL**

## Two Driver Options (both support CSF)

| Driver | Source | Version |
|--------|--------|---------|
| **ARM Official** | `F:/platform-tools/driver/product/kernel/drivers/gpu/arm/` | BX304L01B-r44p1 (newest) |
| **RMX3511 Gondul** | `F:/platform-tools/driver/gondul_mali/` (extracted from 5.4.256) | r41p0+ |

**Recommendation**: Use ARM Official (r44p1) - newer, official Valhall support.

## Build Path (WSL Required)

### Option A: Full Kernel + Module (Cleanest)
```bash
# In WSL Ubuntu:
cd /mnt/f/platform-tools
bash build_mali_csf.sh
```
This script:
1. Clones kernel source (5.4.256 branch - works in Linux)
2. Copies ARM official Mali driver
3. Builds kernel with `RMX3511_athena_defconfig`
4. Builds `mali_kbase.ko` with `CONFIG_MALI_CSF_SUPPORT=y`

### Option B: Module Only (Faster, if kernel matches)
If you can get kernel headers for 5.4.302-NovaKernel:
```bash
# In WSL:
make KDIR=/path/to/kernel/headers \
    CONFIG_MALI_MIDGARD=m \
    CONFIG_MALI_CSF_SUPPORT=y \
    CONFIG_MALI_DEVFREQ=y \
    -j$(nproc)
```

## After Build
```bash
# Test module on device
adb push mali_kbase.ko /data/local/tmp/
adb shell "insmod /data/local/tmp/mali_kbase.ko"

# Check it loaded
adb shell "lsmod | grep mali"
adb shell "dmesg | grep -i mali"

# Verify CSF enabled
adb shell "cat /sys/module/mali_kbase/parameters/csf_support"
```

## Kernel Cmdline (Already Applied - Keep These)
```
module_blacklist=sprd_pmic_wdt mali_kbase.corestack_driver_control=Y mali_kbase.gpu_pollingtime=0
```

## Files Created
- `F:/platform-tools/build_mali_csf.sh` - Main build script (run in WSL)
- `F:/platform-tools/setup_wsl_build.bat` - Run as Admin to install WSL + start build
- `F:/platform-tools/driver/gondul_mali/` - Extracted RMX3511 Mali driver (CSF capable)
- `F:/platform-tools/driver/product/kernel/drivers/gpu/arm/` - ARM official BX304L01B-r44p1 driver

## Next Steps for User
1. **Run as Administrator**: `setup_wsl_build.bat`
2. **After reboot**, Ubuntu opens → run: `cd /mnt/f/platform-tools && bash build_mali_csf.sh`
3. **Wait 30-60 min** for build
4. **Flash new boot.img** or **insmod mali_kbase.ko** for testing