#!/system/bin/sh
# Magisk late_start service to disable sprd_pmic_wdt
# This prevents CM4 PMIC watchdog timeout during reboot on Infinix X6525 (Spreadtrum UMS9230)
# Root cause: sprd_pmic_wdt module causes unclean shutdown corrupting f2fs+FBE on /data

# Wait for boot to complete
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 1
done

# Remove the PMIC watchdog module
# The FIQ watchdog (sprd_wdt_fiq) still provides watchdog functionality
rmmod sprd_pmic_wdt 2>/dev/null

# Log for verification
log -t "DisablePmicWdt" "sprd_pmic_wdt module unloaded (if loaded)"