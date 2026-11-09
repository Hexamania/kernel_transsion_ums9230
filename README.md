# Infinix X6525 (Smart 8) - Mali CSF Kernel Driver Build

> **Root Cause**: Mali-G57 MC2 (Valhall) hardware with Midgard r40p0 kernel driver → missing `callback_power_off_second_part` → GPU power cycling every ~6-60s → Chrome GPU channel timeout → black screen / soft reboot

## Quick Start

### Option 1: Docker (Recommended for Windows)
```bash
# Requires Docker Desktop
cd build/scripts
./build_docker.bat
# Output: ../mali_kbase.ko (with CSF/Valhall support)
```

### Option 2: WSL Ubuntu
```bash
# Requires: wsl --install (reboot required)
cd /mnt/f/platform-tools/build/scripts
bash build_mali_csf.sh
```

### Option 3: GitHub Actions (Cloud)
1. Push this repo to GitHub
2. Actions → Build Mali CSF Module → Run workflow
3. Download `mali_kbase.ko` from artifacts

---

## Repository Structure

```
├── build/
│   ├── docker/
│   │   ├── Dockerfile.mali         # Build container (clang/llvm toolchain)
│   │   └── docker-compose.mali.yml # Compose config
│   └── scripts/
│       ├── build_docker.bat        # Windows Docker launcher
│       ├── build_mali_docker.sh    # Build script (runs in container)
│       ├── build_mali_csf.sh       # Build script (WSL/Linux)
│       └── setup_wsl_build.bat     # WSL installer
├── docs/
│   ├── BUILD_INSTRUCTIONS.md       # Detailed build guide
│   ├── FATAL_summary.md            # Crash analysis
│   └── KERNEL_CMDLINE_GPU_FIX.md   # Kernel cmdline workaround
├── drivers/mali/
│   ├── arm-official/               # ARM BX304L01B-r44p1 (RECOMMENDED)
│   │   └── midgard/                # Midgard driver with CSF support
│   └── gondul-rmx3511/             # RMX3511 vendor driver (extracted)
│       └── midgard/                # Midgard driver with CSF support
├── kernel-patches/                 # Kernel patches (empty - for future)
├── magisk-modules/
│   ├── fix_gpu_pm/                 # Late-start GPU PM fix (boot_completed + 5s)
│   ├── fix_gpu_pm_early/           # Early-start GPU PM fix (immediate)
│   └── disable_pmic_wdt/           # PMIC watchdog disable
├── .github/workflows/
│   └── build-mali.yml              # GitHub Actions CI
└── .gitignore
```

---

## The Fix Explained

### Hardware / Software Mismatch
| Component | Version | Architecture |
|-----------|---------|--------------|
| **GPU Hardware** | Mali-G57 MC2 | **Valhall** (4th gen) |
| **Kernel Driver** | `mali_kbase` r40p0 | **Midgard** (3rd gen) |
| **Userspace Driver** | `libGLES_mali.so` | Valhall ✓ |

**Missing in r40p0**: `backend->callback_power_off_second_part` (NULL) → GPU power cycling

### Solution: Enable CSF (Command Stream Frontend)
```makefile
CONFIG_MALI_MIDGARD=m
CONFIG_MALI_CSF_SUPPORT=y    # ← ENABLES VALHALL SUPPORT
CONFIG_MALI_DEVFREQ=y
```

The **ARM BX304L01B-r44p1** driver (in `drivers/mali/arm-official/`) supports this natively.

---

## Kernel Cmdline Workaround (Already Applied)

If you can't rebuild kernel immediately, add to boot.img cmdline:
```
module_blacklist=sprd_pmic_wdt mali_kbase.corestack_driver_control=Y mali_kbase.gpu_pollingtime=0
```
- `module_blacklist=sprd_pmic_wdt` - Prevents PMIC watchdog reboot corruption
- `mali_kbase.corestack_driver_control=Y` - Bypasses broken PDC integration
- `mali_kbase.gpu_pollingtime=0` - Disables polling that triggers NULL callback

> ⚠️ This is a workaround. Chrome still crashes under load. **Full fix = CSF-enabled kernel driver.**

---

## Building the Module

### Prerequisites
- Linux environment (WSL, Docker, or native Linux)
- Kernel source: `android_kernel_realme_RMX3511` branch `5.4.256`
- ARM Mali driver: `drivers/mali/arm-official/`

### Build Steps (Manual)
```bash
# 1. Get kernel source (Linux only - aux.c issue on Windows)
git clone -b 5.4.256 https://github.com/realme-kernel/android_kernel_realme_RMX3511.git kernel

# 2. Copy Mali driver
cp -r drivers/mali/arm-official kernel/kernel_modules/kernel5.4/gpu/gondul/mali_new

# 3. Build kernel
cd kernel
source setup.env
./build.sh config-dev
./build.sh compile

# 4. Build Mali module with CSF
cd kernel_modules/kernel5.4/gpu/gondul/mali_new
make KDIR=../../../../out \
    CONFIG_MALI_MIDGARD=m \
    CONFIG_MALI_CSF_SUPPORT=y \
    CONFIG_MALI_DEVFREQ=y \
    CONFIG_MALI_GATOR_SUPPORT=y \
    CONFIG_MALI_DEBUG=n \
    -j$(nproc)

# 5. Result: mali_kbase.ko
```

---

## Testing on Device

```bash
# Push and load module
adb push mali_kbase.ko /data/local/tmp/
adb shell "insmod /data/local/tmp/mali_kbase.ko"

# Verify
adb shell "lsmod | grep mali"
adb shell "dmesg -T | grep -i -e mali -e csf"

# Expected: "CSF firmware loaded" or "CSF support enabled"
```

---

## Magisk Modules (Workarounds)

| Module | Type | Description |
|--------|------|-------------|
| `fix_gpu_pm` | late_start | Runs at `boot_completed + 5s` - too late for boot GPU init |
| `fix_gpu_pm_early` | early_start | Runs immediately at boot - **recommended** |
| `disable_pmic_wdt` | late_start | Removes `sprd_pmic_wdt` after boot |

Install via Magisk/KernelSU → Modules → Install from storage.

---

## Device Info

- **Device**: Infinix Smart 8 (X6525)
- **SoC**: Unisoc UMS9230 / T606
- **GPU**: Mali-G57 MC2 (Valhall)
- **Port Base**: Samsung Galaxy S24 FE (SM-S721B, One UI 9.0, Android 17)
- **Current Kernel**: 5.4.302-NovaKernel/4fa94bab

---

## Related Memories

- `infinix-x6525-port-debug` - Project overview
- `infinix-x6525-reboot-fix` - PMIC watchdog root cause
- `infinix-x6525-gpu-fix` - GPU driver mismatch details

---

## License

Kernel driver: GPL-2.0 (ARM Mali)
Build scripts: MIT