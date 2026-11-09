#!/system/bin/sh
# Magisk late_start service to fix GPU power management
# Workaround for Mali-G57 (Valhall) with Midgard r40p0 kernel driver
# Prevents GPU power cycling that causes "Timed out waiting for GPU channel" in Chrome

# Wait for boot to complete
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 1
done

# Give system time to settle
sleep 5

GPU_PATH="/sys/devices/platform/soc/soc:mm/23100000.gpu"

# Disable GPU runtime PM
if [ -f "$GPU_PATH/power/control" ]; then
    echo on > "$GPU_PATH/power/control" 2>/dev/null
    log -t "FixGpuPm" "Set GPU power/control = on"
fi

# Set GPU devfreq governor to performance
if [ -f "$GPU_PATH/devfreq/23100000.gpu/governor" ]; then
    echo performance > "$GPU_PATH/devfreq/23100000.gpu/governor" 2>/dev/null
    log -t "FixGpuPm" "Set GPU devfreq governor = performance"
fi

# Try to set kbase power_policy to always_on (may not work at runtime)
if [ -f "$GPU_PATH/power_policy" ]; then
    echo always_on > "$GPU_PATH/power_policy" 2>/dev/null
    log -t "FixGpuPm" "Attempted to set kbase power_policy = always_on"
fi

# Disable mali_kbase polling (read-only at runtime, but try)
if [ -f /sys/module/mali_kbase/parameters/gpu_pollingtime ]; then
    echo 0 > /sys/module/mali_kbase/parameters/gpu_pollingtime 2>/dev/null
    log -t "FixGpuPm" "Set mali_kbase gpu_pollingtime = 0"
fi

log -t "FixGpuPm" "GPU power management workaround applied"