from dataclasses import dataclass
from ctypes import *

import time

from prometheus_client import start_http_server, Gauge

import logging
from pyrsmi import rocml

logger = logging.getLogger(__name__)


import platform
HOSTNAME = platform.node()

LABEL_UID = "uid"
LABEL_PCI_ID = "pciId"
LABEL_GPU = "gpu"
LABEL_MODEL_NAME = "modelName"
LABEL_HOSTNAME = "Hostname"
LABEL_RSMI_VERSION = "rsmiVersion"
LABEL_ROCM_KERNEL_VERSION = "rocmKernelVersion"
COMMON_LABELS = [LABEL_HOSTNAME, LABEL_RSMI_VERSION, LABEL_ROCM_KERNEL_VERSION]
LABELS = [LABEL_UID, LABEL_PCI_ID, LABEL_GPU, LABEL_MODEL_NAME, LABEL_HOSTNAME, LABEL_RSMI_VERSION, LABEL_ROCM_KERNEL_VERSION]

def _get_common_labels():
    """
    Returns a dict of the common labels for metric
    """
    res = {}
    res[LABEL_HOSTNAME] = HOSTNAME
    res[LABEL_RSMI_VERSION] = rocml.smi_get_version()
    res[LABEL_ROCM_KERNEL_VERSION] = rocml.smi_get_kernel_version()
    return res

# These names are mimicing dcgm-exporter:
# DCGM_FI_DEV_GPU_UTIL and DCGM_FI_DEV_MEM_COPY_UTIL
METRIC_GPU_COUNT = "ROCM_SMI_DEV_GPU_COUNT"
METRIC_GPU_UTIL = "ROCM_SMI_DEV_GPU_UTIL"
METRIC_GPU_MEM_TOTAL = "ROCM_SMI_DEV_GPU_MEM_TOTAL"
METRIC_GPU_MEM_USED = "ROCM_SMI_DEV_GPU_MEM_USED"
METRIC_GPU_MEM_UTIL = "ROCM_SMI_DEV_MEM_UTIL"
METRIC_GPU_POWER = "ROCM_SMI_DEV_POWER"
METRIC_GPU_CU_OCCUPANCY = "ROCM_SMI_DEV_CU_OCCUPANCY"
METRIC_GPU_TEMP = "ROCM_SMI_DEV_TEMP"
METRIC_GPU_POWER = "ROCM_SMI_DEV_POWER"

def smi_get_device_pci_id(dev):
    """returns unique PCI ID of the device in 64bit Hex with format:
       BDFID = ((DOMAIN & 0xffffffff) << 32) | ((BUS & 0xff) << 8) |
                    ((DEVICE & 0x1f) <<3 ) | (FUNCTION & 0x7)
                    
    This was adapted from smi_get_device_pci_id() in
    https://github.com/ROCm/pyrsmi/blob/main/pyrsmi/rocml.py
    """
    bdfid = c_uint64()
    ret = rocml.rocm_lib.rsmi_dev_pci_id_get(dev, byref(bdfid))
    return bdfid.value if rocml.rsmi_ret_ok(ret) else -1

def format_pci_id(dev: int):
    """Format device_bus_id as fixed format string.

    :param device_bus_id: Device/GPU's PCI bus ID
    :return formatted GPU ID
    
    This was adapted from getBus() in
    github.com/ROCm/rocm_smi_lib/blob/amd-staging/python_smi_tools/rocm_smi.py
    
    AMD's device plugin uses this formated bus ID as device identifier.
    NVIDIA uses GPU's uuid.
    """
    device_bus_id = smi_get_device_pci_id(dev)
    domain = (device_bus_id >> 32) & 0xffffffff
    bus = (device_bus_id >> 8) & 0xff
    device = (device_bus_id >> 3) & 0x1f
    function = device_bus_id & 0x7
    return '{:04X}:{:02X}:{:02X}.{:0X}'.format(domain, bus, device, function)

temp_type_lst = ['edge', 'junction', 'memory', 'HBM 0', 'HBM 1', 'HBM 2', 'HBM 3']

def getTemp(device, sensor):
    """ Display the current temperature from a given device's sensor

    :param device: DRM device identifier
    :param sensor: Temperature sensor identifier
    :param silent: Turn on to silence error output
        (you plan to handle manually). Default is on.
    """
    temp = c_int64(0)
    RSMI_TEMP_CURRENT = 0x0
    SENSOR_INDEX = 1 # for junction
    print("test1")
    ret = rocml.rocm_lib.rsmi_dev_temp_metric_get(c_uint32(device), SENSOR_INDEX, RSMI_TEMP_CURRENT, byref(temp))
    print("test2")
    if rocml.rsmi_ret_ok(ret):
        print("test3")
        return temp.value / 1000
    print("test4")
    return -1


class GPUMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    @dataclass
    class Config:
        port: int
        polling_interval_seconds: int

    def __init__(self, config: Config):
        self.config = config

        rocml.smi_initialize()

        self.common_labels = _get_common_labels()

        # Define Prometheus metrics to collect
        self.gpu_count = Gauge(METRIC_GPU_COUNT, "GPU count.", COMMON_LABELS)

        self.gpu_util = Gauge(METRIC_GPU_UTIL, "GPU utilization (in %).", LABELS)
        self.gpu_mem_used = Gauge(METRIC_GPU_MEM_USED, "GPU memory used (in Byte).", LABELS)
        self.gpu_mem_total = Gauge(METRIC_GPU_MEM_TOTAL, "GPU memory total (in Byte).", LABELS)
        self.gpu_mem_util = Gauge(METRIC_GPU_MEM_UTIL, "GPU memory utilization (in %).", LABELS)
        self.gpu_cu_occupancy = Gauge(METRIC_GPU_CU_OCCUPANCY, "GPU CU occupancy (in %).", LABELS)
        self.gpu_temp = Gauge(METRIC_GPU_TEMP, "GPU temperature (in c).", LABELS)
        self.gpu_power = Gauge(METRIC_GPU_POWER, "GPU power, (in W).", LABELS)

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        logger.info(f"Starting expoerter on :{self.config.port}")
        start_http_server(self.config.port)
        while True:
            logger.info(f"Fetching metrics ...")
            self.fetch()
            time.sleep(self.config.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics.
        """
        labels = self.common_labels.copy()

        ngpus = rocml.smi_get_device_count()
        self.gpu_count.labels(**labels).set(ngpus)

        for dev in range(ngpus):
            uid = rocml.smi_get_device_unique_id(dev)
            dev_model_name = rocml.smi_get_device_name(dev)
            pci_id = format_pci_id(dev)
            
            labels[LABEL_UID] = uid
            labels[LABEL_PCI_ID] = pci_id
            labels[LABEL_GPU] = dev
            labels[LABEL_MODEL_NAME] = dev_model_name

            util = rocml.smi_get_device_utilization(dev)
            self.gpu_util.labels(**labels).set(util)

            mem_used = rocml.smi_get_device_memory_used(dev)
            self.gpu_mem_used.labels(**labels).set(mem_used)

            mem_total = rocml.smi_get_device_memory_total(dev)
            self.gpu_mem_total.labels(**labels).set(mem_total)

            mem_ratio = mem_used / mem_total
            self.gpu_mem_util.labels(**labels).set(mem_ratio)

            cu_occupancy = smi_get_device_cu_occupancy(dev)
            self.gpu_cu_occupancy.labels(**labels).set(cu_occupancy)
            
            temp = getTemp(dev, 'junction')
            self.gpu_temp.labels(**labels).set(temp)
            
            power = rocml.smi_get_device_average_power(dev)
            self.gpu_power.labels(**labels).set(power)


def smi_get_device_cu_occupancy(dev):
    """returns list of process ids running compute on the device dev"""
    num_procs = rocml.c_uint32()
    ret = rocml.rocm_lib.rsmi_compute_process_info_get(None, rocml.byref(num_procs))
    if rocml.rsmi_ret_ok(ret):
        buff_sz = num_procs.value + 10
        proc_info = (rocml.rsmi_process_info_t * buff_sz)()
        ret2 = rocml.rocm_lib.rsmi_compute_process_info_get(rocml.byref(proc_info), rocml.byref(num_procs))

        return sum(proc_info[i].cu_occupancy for i in range(num_procs.value)) if rocml.rsmi_ret_ok(ret2) else 0
    else:
        return 0

import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Parse command line arguments for port and polling interval.')

    parser.add_argument('--port', type=int, default=9001, help='Port number to use.')
    parser.add_argument('--polling-interval-seconds', type=int, default=5, help='Polling interval in seconds.')

    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    app_metrics = GPUMetrics(
        GPUMetrics.Config(
            port=args.port,
            polling_interval_seconds=args.polling_interval_seconds
        )
    )
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()
