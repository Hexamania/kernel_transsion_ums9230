#!/system/bin/sh
# Magisk early_start service - runs at boot BEFORE SurfaceFlinger
# Fixes GPU power management for Mali-G57 (Valhall) with Midgard r40p0 kernel driver

GPU_PATH="/sys/devices/platform/soc/soc:mm/23100000.gpu"

# Disable GPU runtime PM immediately
if [ -f "$GPU_PATH/power/control" ]; then
    echo on > "$GPU_PATH/power/control" 2>/dev/null
    log -t "FixGpuPmEarly" "Set GPU power/control = on"
fi

# Set GPU devfreq governor to performance
if [ -f "$GPU_PATH/devfreq/23100000.gpu/governor" ]; then
    echo performance > "$GPU_PATH/devfreq/23100000.gpu/governor" 2>/dev/null
    log -t "FixGpuPmEarly" "Set GPU devfreq governor = performance"
fi

# Set kbase power_policy to always_on
if [ -f "$GPU_PATH/power_policy" ]; then
    echo always_on > "$GPU_PATH/power_policy" 2>/dev/null
    log -t "FixGpuPmEarly" "Set kbase power_policy = always_on"
fi

# Disable mali_kbase polling
if [ -f /sys/module/mali_kbase/parameters/gpu_pollingtime ]; then
    echo 0 > /sys/module/mali_kbase/parameters/gpu_pollingtime 2>/dev/null
    log -t "FixGpuPmEarly" "Set mali_kbase gpu_pollingtime = 0"
fi

log -t "FixGpuPmEarly" "GPU power management fix applied at early boot"
