/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */
/*
 * Compatibility header for mali_kbase_csf_errors_dumpfault
 * This header provides the necessary definitions for kernels that don't have
 * the CSF UAPI headers.
 *
 * (C) COPYRIGHT 2022-2023 ARM Limited. All rights reserved.
 */

#ifndef _UAPI_GPU_ARM_MIDGARD_CSF_MALI_KBASE_CSF_ERRORS_DUMPFAULT_H_
#define _UAPI_GPU_ARM_MIDGARD_CSF_MALI_KBASE_CSF_ERRORS_DUMPFAULT_H_

#include <linux/types.h>

/* CSF fault dump error codes */
enum mali_kbase_csf_error_dumpfault {
	MALI_KBASE_CSF_ERROR_DUMPFAULT_NONE = 0,
	MALI_KBASE_CSF_ERROR_DUMPFAULT_GENERIC = 1,
	MALI_KBASE_CSF_ERROR_DUMPFAULT_TIMEOUT = 2,
	MALI_KBASE_CSF_ERROR_DUMPFAULT_OOM = 3,
	MALI_KBASE_CSF_ERROR_DUMPFAULT_INVALID = 4,
};

/* CSF fault dump structure */
struct mali_kbase_csf_error_dumpfault {
	__u32 error_type;
	__u32 fault_address;
	__u32 fault_status;
	__u32 fault_extra;
	__u64 timestamp;
	__u32 reserved[4];
};

#endif /* _UAPI_GPU_ARM_MIDGARD_CSF_MALI_KBASE_CSF_ERRORS_DUMPFAULT_H_ */