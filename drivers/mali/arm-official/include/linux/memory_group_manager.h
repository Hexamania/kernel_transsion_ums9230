/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */
/*
 * Compatibility header for memory_group_manager
 * This header provides the necessary definitions for kernels that don't have
 * the memory_group_manager subsystem (introduced in Linux 6.6).
 *
 * (C) COPYRIGHT 2022-2023 ARM Limited. All rights reserved.
 */

#ifndef _LINUX_MEMORY_GROUP_MANAGER_COMPAT_H_
#define _LINUX_MEMORY_GROUP_MANAGER_COMPAT_H_

#include <linux/types.h>
#include <linux/mm.h>
#include <linux/dma-buf.h>

/* Maximum number of memory groups */
#define MEMORY_GROUP_MANAGER_NR_GROUPS		32

/* Memory group manager import types */
enum memory_group_manager_import_type {
	MEMORY_GROUP_MANAGER_IMPORT_TYPE_DMA_BUF = 0,
	MEMORY_GROUP_MANAGER_IMPORT_TYPE_MAX,
};

/* Import data structure */
struct memory_group_manager_import_data {
	enum memory_group_manager_import_type type;
	union {
		struct dma_buf *dma_buf;
	} u;
};

/* Memory group manager device structure */
struct memory_group_manager_device {
	struct module *owner;
	struct device *dev;
	const struct memory_group_manager_ops *ops;
	void *data;
};

/* Memory group manager operations */
struct memory_group_manager_ops {
	struct page * (*mgm_alloc_page)(struct memory_group_manager_device *mgm_dev,
					int group_id, gfp_t gfp_mask, unsigned int order);
	void (*mgm_free_page)(struct memory_group_manager_device *mgm_dev,
			      int group_id, struct page *page, unsigned int order);
	int (*mgm_get_import_memory_id)(struct memory_group_manager_device *mgm_dev,
					struct memory_group_manager_import_data *import_data);
	vm_fault_t (*mgm_vmf_insert_pfn_prot)(struct memory_group_manager_device *mgm_dev,
					      int group_id, struct vm_area_struct *vma,
					      unsigned long addr, unsigned long pfn, pgprot_t pgprot);
	u64 (*mgm_update_gpu_pte)(struct memory_group_manager_device *mgm_dev,
				  int group_id, int mmu_level, u64 pte);
	u64 (*mgm_pte_to_original_pte)(struct memory_group_manager_device *mgm_dev,
				       int group_id, int mmu_level, u64 pte);
};

#endif /* _LINUX_MEMORY_GROUP_MANAGER_COMPAT_H_ */