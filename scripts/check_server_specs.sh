#!/usr/bin/env bash
# Check server specs (CPU, RAM, GPU, disk). Run on the server, e.g. via SSH.
# Usage: bash check_server_specs.sh   or   ./check_server_specs.sh

set -e

echo "========== SERVER SPECS =========="
echo ""

echo "--- Hostname ---"
hostname 2>/dev/null || echo "(unknown)"
echo ""

echo "--- OS ---"
if [ -f /etc/os-release ]; then
  . /etc/os-release && echo "$PRETTY_NAME"
else
  uname -s
fi
echo ""

echo "--- CPU ---"
if command -v lscpu &>/dev/null; then
  lscpu | grep -E "Model name|Socket|Core|Thread|CPU\(s\)"
else
  grep -m1 "model name" /proc/cpuinfo 2>/dev/null || sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "n/a"
fi
echo ""

echo "--- RAM ---"
if command -v free &>/dev/null; then
  free -h | head -2
else
  echo "Total: $(sysctl -n hw.memsize 2>/dev/null | awk '{print $0/1024/1024/1024 " GB"}')"
fi
echo ""

echo "--- GPU (NVIDIA) ---"
if command -v nvidia-smi &>/dev/null; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || nvidia-smi
else
  echo "No nvidia-smi (no NVIDIA GPU or drivers not installed)"
fi
echo ""

echo "--- GPU (other) ---"
if [ -d /sys/class/drm ]; then
  ls /sys/class/drm 2>/dev/null | grep -E "card[0-9]" | head -5 || true
fi
echo ""

echo "--- Disk ---"
df -h / 2>/dev/null || df -h .
echo ""

echo "--- VM or physical? ---"
if command -v systemd-detect-virt &>/dev/null; then
  v=$(systemd-detect-virt 2>/dev/null)
  if [ "$v" = "none" ]; then
    echo "Virt: none (likely physical hardware)"
  else
    echo "Virt: $v (virtual machine)"
  fi
else
  echo "systemd-detect-virt not available"
fi
if [ -r /sys/class/dmi/id/sys_vendor ]; then
  echo "DMI sys_vendor:  $(cat /sys/class/dmi/id/sys_vendor 2>/dev/null)"
  echo "DMI product:    $(cat /sys/class/dmi/id/product_name 2>/dev/null)"
  echo "DMI chassis:    $(cat /sys/class/dmi/id/chassis_type 2>/dev/null)"
fi
echo "Optional (with sudo): dmidecode -t system -t chassis"
echo ""

echo "========== DONE =========="
