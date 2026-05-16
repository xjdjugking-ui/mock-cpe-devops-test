"""Mock 硬件控制层 — 继电器、TFTP 服务、抓包

极简 Mock：所有操作均为 print 日志 + 返回 True/False。
用于模拟真机测试环境中的硬件自动化操作。
"""
import random
import time


class PowerRelay:
    """Mock 继电器：控制设备上下电。"""

    def __init__(self, device_name: str = "DUT-01", failure_rate: float = 0.005):
        self.device_name = device_name
        self._failure_rate = failure_rate
        self._powered = False

    def power_on(self) -> bool:
        time.sleep(0.5)
        if random.random() < self._failure_rate:
            print(f"[Relay:{self.device_name}] power_on FAILED (fault injected)")
            return False
        self._powered = True
        print(f"[Relay:{self.device_name}] power_on OK")
        return True

    def power_off(self) -> bool:
        time.sleep(0.3)
        if random.random() < self._failure_rate:
            print(f"[Relay:{self.device_name}] power_off FAILED (fault injected)")
            return False
        self._powered = False
        print(f"[Relay:{self.device_name}] power_off OK")
        return True

    def power_cycle(self, off_delay: float = 2.0) -> bool:
        """冷重启：先断电 → 等待 → 上电"""
        print(f"[Relay:{self.device_name}] power_cycle START (off_delay={off_delay}s)")
        self.power_off()
        time.sleep(off_delay)
        return self.power_on()

    def is_powered(self) -> bool:
        return self._powered


class TftpServer:
    """Mock TFTP 服务器：用于设备下载固件。"""

    def __init__(self, server_dir: str = "/srv/tftp", failure_rate: float = 0.005):
        self.server_dir = server_dir
        self._failure_rate = failure_rate
        self._running = False

    def start(self) -> bool:
        print(f"[TFTP] start server at {self.server_dir}")
        self._running = True
        return True

    def stop(self) -> bool:
        print(f"[TFTP] stop server at {self.server_dir}")
        self._running = False
        return True

    def upload_file(self, local_path: str, remote_name: str = "") -> bool:
        time.sleep(0.3)
        if random.random() < self._failure_rate:
            print(f"[TFTP] upload FAILED: {local_path} (fault injected)")
            return False
        name = remote_name or local_path.rsplit("/", 1)[-1]
        print(f"[TFTP] uploaded {local_path} -> {self.server_dir}/{name}")
        return True

    def is_running(self) -> bool:
        return self._running


class PacketCapture:
    """Mock 抓包工具：模拟 tcpdump 抓取设备网络流量。"""

    def __init__(self, interface: str = "eth0", pcap_dir: str = "/tmp/pcaps"):
        self.interface = interface
        self.pcap_dir = pcap_dir
        self._capturing = False
        self._packets = 0

    def start_capture(self, filename: str = "capture.pcap") -> bool:
        print(f"[Pcap] start {self.interface} -> {self.pcap_dir}/{filename}")
        self._capturing = True
        self._packets = 0
        return True

    def stop_capture(self) -> str:
        self._capturing = False
        self._packets = random.randint(120, 8500)
        filename = f"{self.pcap_dir}/capture_{int(time.time())}.pcap"
        print(f"[Pcap] stopped ({self._packets} packets) -> {filename}")
        return filename

    def packet_count(self) -> int:
        return self._packets

    def is_capturing(self) -> bool:
        return self._capturing