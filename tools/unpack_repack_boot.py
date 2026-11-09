#!/usr/bin/env python3
"""
Unpack and repack Android boot image, modifying kernel cmdline.
"""

import struct
import os
import sys

# Boot image header format (Android 9+ / boot header v1+)
# struct boot_img_hdr {
#     uint8_t magic[8];           // "ANDROID!"
#     uint32_t kernel_size;       // size of kernel in bytes
#     uint32_t kernel_addr;       // load address of kernel
#     uint32_t ramdisk_size;      // size of ramdisk in bytes
#     uint32_t ramdisk_addr;      // load address of ramdisk
#     uint32_t second_size;       // size of second stage in bytes
#     uint32_t second_addr;       // load address of second stage
#     uint32_t tags_addr;         // kernel tags address
#     uint32_t page_size;         // flash page size
#     uint32_t header_version;    // boot header version
#     uint32_t os_version;        // os version (9.0+)
#     uint8_t name[16];           // name of this boot image
#     uint8_t cmdline[512];       // kernel cmdline
#     uint32_t id[8];             # sha1 digest
#     uint8_t extra_cmdline[1024]; # additional cmdline (v1+)
#     uint32_t recovery_dtbo_size; # recovery dtbo size (v1+)
#     uint64_t recovery_dtbo_offset; # recovery dtbo offset (v1+)
#     uint32_t header_size;       # size of header (v1+)
# }

BOOT_MAGIC = b'ANDROID!'
BOOT_MAGIC_SIZE = 8
BOOT_NAME_SIZE = 16
BOOT_ARGS_SIZE = 512
BOOT_EXTRA_ARGS_SIZE = 1024

def read_boot_image(path):
    with open(path, 'rb') as f:
        data = f.read()

    # Parse header
    if data[:8] != BOOT_MAGIC:
        raise ValueError("Not a valid Android boot image")

    # Unpack header (first 1556 bytes for v1+)
    header_fmt = '<8sIIIIIIIIII16s512s8s1024sIIQI'
    header_size = struct.calcsize(header_fmt)

    if len(data) < header_size:
        raise ValueError("Boot image too small for header")

    hdr = struct.unpack(header_fmt, data[:header_size])

    magic = hdr[0]
    kernel_size = hdr[1]
    kernel_addr = hdr[2]
    ramdisk_size = hdr[3]
    ramdisk_addr = hdr[4]
    second_size = hdr[5]
    second_addr = hdr[6]
    tags_addr = hdr[7]
    page_size = hdr[8]
    header_version = hdr[9]
    os_version = hdr[10]
    name = hdr[11].rstrip(b'\x00')
    cmdline = hdr[12].rstrip(b'\x00')
    id_hash = hdr[13]
    extra_cmdline = hdr[14].rstrip(b'\x00')
    recovery_dtbo_size = hdr[15]
    recovery_dtbo_offset = hdr[16]
    header_size_field = hdr[17]

    # Calculate offsets
    page_mask = page_size - 1
    kernel_offset = header_size_field
    kernel_pages = (kernel_size + page_mask) // page_size
    ramdisk_offset = kernel_offset + kernel_pages * page_size
    ramdisk_pages = (ramdisk_size + page_mask) // page_size
    second_offset = ramdisk_offset + ramdisk_pages * page_size
    second_pages = (second_size + page_mask) // page_size

    # Extract components
    kernel = data[kernel_offset:kernel_offset + kernel_size]
    ramdisk = data[ramdisk_offset:ramdisk_offset + ramdisk_size]
    second = data[second_offset:second_offset + second_size] if second_size > 0 else b''

    # DTB extraction (if present, usually in recovery_dtbo for v1+)
    dtb = b''
    if recovery_dtbo_size > 0 and recovery_dtbo_offset > 0:
        dtb = data[recovery_dtbo_offset:recovery_dtbo_offset + recovery_dtbo_size]

    return {
        'magic': magic,
        'kernel_size': kernel_size,
        'kernel_addr': kernel_addr,
        'ramdisk_size': ramdisk_size,
        'ramdisk_addr': ramdisk_addr,
        'second_size': second_size,
        'second_addr': second_addr,
        'tags_addr': tags_addr,
        'page_size': page_size,
        'header_version': header_version,
        'os_version': os_version,
        'name': name,
        'cmdline': cmdline.decode('utf-8', errors='ignore'),
        'extra_cmdline': extra_cmdline.decode('utf-8', errors='ignore'),
        'id_hash': id_hash,
        'recovery_dtbo_size': recovery_dtbo_size,
        'recovery_dtbo_offset': recovery_dtbo_offset,
        'header_size': header_size_field,
        'kernel': kernel,
        'ramdisk': ramdisk,
        'second': second,
        'dtb': dtb,
        'page_mask': page_mask,
    }

def write_boot_image(path, info):
    page_size = info['page_size']
    page_mask = page_size - 1

    # Combine cmdline and extra_cmdline
    full_cmdline = (info['cmdline'] + ' ' + info['extra_cmdline']).strip()
    full_cmdline_bytes = full_cmdline.encode('utf-8')

    # Build header
    header_version = info['header_version']
    header_size = info['header_size']

    # Pad cmdline to 512 bytes
    cmdline_padded = full_cmdline_bytes[:511] + b'\x00' * (512 - min(len(full_cmdline_bytes), 511))

    # Pad extra_cmdline to 1024 bytes
    extra_cmdline_padded = full_cmdline_bytes[512:512+1023] + b'\x00' * (1024 - min(len(full_cmdline_bytes) - 512, 1023)) if len(full_cmdline_bytes) > 512 else b'\x00' * 1024

    # Calculate offsets
    kernel_pages = (info['kernel_size'] + page_mask) // page_size
    ramdisk_pages = (info['ramdisk_size'] + page_mask) // page_size
    second_pages = (info['second_size'] + page_mask) // page_size

    kernel_offset = header_size
    ramdisk_offset = kernel_offset + kernel_pages * page_size
    second_offset = ramdisk_offset + ramdisk_pages * page_size

    # Recovery DTBO
    recovery_dtbo_size = info['recovery_dtbo_size']
    recovery_dtbo_offset = info['recovery_dtbo_offset']
    if recovery_dtbo_size > 0:
        recovery_dtbo_pages = (recovery_dtbo_size + page_mask) // page_size
        # DTBO typically after second
        if recovery_dtbo_offset == 0:
            recovery_dtbo_offset = second_offset + second_pages * page_size
    else:
        recovery_dtbo_size = 0
        recovery_dtbo_offset = 0

    # Pack header
    hdr = struct.pack(
        '<8sIIIIIIIIII16s512s8s1024sIIQI',
        BOOT_MAGIC,
        info['kernel_size'],
        info['kernel_addr'],
        info['ramdisk_size'],
        info['ramdisk_addr'],
        info['second_size'],
        info['second_addr'],
        info['tags_addr'],
        page_size,
        header_version,
        info['os_version'],
        info['name'][:15].ljust(16, b'\x00'),
        cmdline_padded,
        info['id_hash'],
        extra_cmdline_padded,
        recovery_dtbo_size,
        recovery_dtbo_offset,
        header_size
    )

    # Pad header to header_size
    hdr = hdr.ljust(header_size, b'\x00')

    # Write image
    with open(path, 'wb') as f:
        f.write(hdr)
        f.write(info['kernel'])
        f.write(b'\x00' * (kernel_pages * page_size - info['kernel_size']))
        f.write(info['ramdisk'])
        f.write(b'\x00' * (ramdisk_pages * page_size - info['ramdisk_size']))
        if info['second_size'] > 0:
            f.write(info['second'])
            f.write(b'\x00' * (second_pages * page_size - info['second_size']))
        if recovery_dtbo_size > 0:
            f.write(info['dtb'])
            f.write(b'\x00' * (recovery_dtbo_pages * page_size - recovery_dtbo_size))

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 unpack_repack_boot.py <input> <output> <new_cmdline>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    new_cmdline = sys.argv[3]

    info = read_boot_image(input_path)

    print(f"Original cmdline: {info['cmdline']}")
    print(f"Original extra_cmdline: {info['extra_cmdline']}")
    print(f"Header version: {info['header_version']}")
    print(f"Page size: {info['page_size']}")
    print(f"Kernel size: {info['kernel_size']}")
    print(f"Ramdisk size: {info['ramdisk_size']}")

    # Update cmdline
    info['cmdline'] = new_cmdline
    info['extra_cmdline'] = ''  # Put everything in cmdline

    print(f"New cmdline: {new_cmdline}")

    write_boot_image(output_path, info)
    print(f"Written to {output_path}")

if __name__ == '__main__':
    main()