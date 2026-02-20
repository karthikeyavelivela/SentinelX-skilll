#!/usr/bin/env python3
"""
VulnGuard AI Endpoint Agent
Cross-platform system inventory agent that reports to the backend.
Supports Windows, Linux, and macOS.
"""

import platform
import socket
import uuid
import time
import json
import sys
import os
import subprocess
import logging
from typing import List, Dict, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VulnGuard-Agent] %(levelname)s: %(message)s",
)
logger = logging.getLogger("vulnguard-agent")

# ── Configuration ──
BACKEND_URL = os.environ.get("VULNGUARD_BACKEND_URL", "http://localhost:8000")
AGENT_TOKEN = os.environ.get("VULNGUARD_AGENT_TOKEN", "")
HEARTBEAT_INTERVAL = int(os.environ.get("VULNGUARD_HEARTBEAT_INTERVAL", "300"))


class SystemCollector:
    """Collect system information."""

    def __init__(self):
        self.os_platform = platform.system().lower()
        self.agent_id = self._get_agent_id()

    def _get_agent_id(self) -> str:
        id_file = os.path.expanduser("~/.vulnguard_agent_id")
        if os.path.exists(id_file):
            with open(id_file) as f:
                return f.read().strip()
        agent_id = str(uuid.uuid4())
        with open(id_file, "w") as f:
            f.write(agent_id)
        return agent_id

    def get_os_info(self) -> Dict:
        return {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_platform": self.os_platform,
            "hostname": socket.gethostname(),
            "architecture": platform.machine(),
        }

    def get_network_info(self) -> Dict:
        ip = "127.0.0.1"
        mac = ""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            pass

        if HAS_PSUTIL:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        mac = addr.address
                        break
                if mac:
                    break

        return {"ip_address": ip, "mac_address": mac}

    def get_open_ports(self) -> List[int]:
        ports = []
        if HAS_PSUTIL:
            for conn in psutil.net_connections(kind="inet"):
                if conn.status == "LISTEN" and conn.laddr:
                    ports.append(conn.laddr.port)
        return sorted(set(ports))

    def get_installed_software(self) -> List[Dict]:
        software = []
        
        if self.os_platform == "linux":
            software.extend(self._get_dpkg_packages())
            software.extend(self._get_rpm_packages())
        elif self.os_platform == "windows":
            software.extend(self._get_windows_software())
        elif self.os_platform == "darwin":
            software.extend(self._get_macos_software())
        
        return software

    def _get_dpkg_packages(self) -> List[Dict]:
        packages = []
        try:
            output = subprocess.check_output(
                ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Status}\n"],
                stderr=subprocess.DEVNULL, text=True,
            )
            for line in output.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2 and "installed" in (parts[2] if len(parts) > 2 else "installed"):
                    packages.append({
                        "name": parts[0], "version": parts[1],
                        "vendor": "debian", "is_service": False,
                    })
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return packages

    def _get_rpm_packages(self) -> List[Dict]:
        packages = []
        try:
            output = subprocess.check_output(
                ["rpm", "-qa", "--queryformat", "%{NAME}\t%{VERSION}-%{RELEASE}\t%{VENDOR}\n"],
                stderr=subprocess.DEVNULL, text=True,
            )
            for line in output.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    packages.append({
                        "name": parts[0], "version": parts[1],
                        "vendor": parts[2] if len(parts) > 2 else "",
                        "is_service": False,
                    })
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return packages

    def _get_windows_software(self) -> List[Dict]:
        packages = []
        try:
            output = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
                 "Select-Object DisplayName, DisplayVersion, Publisher | ConvertTo-Json"],
                stderr=subprocess.DEVNULL, text=True,
            )
            items = json.loads(output)
            if isinstance(items, dict):
                items = [items]
            for item in items:
                if item.get("DisplayName"):
                    packages.append({
                        "name": item["DisplayName"],
                        "version": item.get("DisplayVersion", ""),
                        "vendor": item.get("Publisher", ""),
                        "is_service": False,
                    })
        except:
            pass
        return packages

    def _get_macos_software(self) -> List[Dict]:
        packages = []
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPApplicationsDataType", "-json"],
                stderr=subprocess.DEVNULL, text=True,
            )
            data = json.loads(output)
            for app in data.get("SPApplicationsDataType", []):
                packages.append({
                    "name": app.get("_name", ""),
                    "version": app.get("version", ""),
                    "vendor": app.get("obtained_from", ""),
                    "is_service": False,
                })
        except:
            pass
        return packages

    def get_running_services(self) -> List[Dict]:
        services = []
        if HAS_PSUTIL:
            for proc in psutil.process_iter(["pid", "name", "username", "status"]):
                try:
                    info = proc.info
                    connections = proc.connections()
                    for conn in connections:
                        if conn.status == "LISTEN":
                            services.append({
                                "name": info["name"],
                                "pid": info["pid"],
                                "port": conn.laddr.port,
                                "protocol": "tcp",
                                "status": info["status"],
                                "user": info["username"] or "",
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return services

    def get_patch_level(self) -> str:
        if self.os_platform == "linux":
            try:
                output = subprocess.check_output(
                    ["uname", "-r"], stderr=subprocess.DEVNULL, text=True
                )
                return output.strip()
            except:
                pass
        elif self.os_platform == "windows":
            return platform.version()
        return "unknown"

    def collect_all(self) -> Dict:
        os_info = self.get_os_info()
        net_info = self.get_network_info()
        
        return {
            "hostname": os_info["hostname"],
            "agent_id": self.agent_id,
            "agent_version": "1.0.0",
            "os_name": os_info["os_name"],
            "os_version": os_info["os_version"],
            "os_platform": os_info["os_platform"],
            "ip_address": net_info["ip_address"],
            "mac_address": net_info["mac_address"],
            "open_ports": self.get_open_ports(),
            "installed_software": self.get_installed_software()[:200],
            "running_services": self.get_running_services()[:100],
            "patch_level": self.get_patch_level(),
        }


class AgentClient:
    """Communicate with VulnGuard backend."""

    def __init__(self, backend_url: str, token: str):
        self.backend_url = backend_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}" if token else "",
        }

    def register(self, data: Dict) -> bool:
        try:
            resp = requests.post(
                f"{self.backend_url}/api/assets/agent/register",
                json=data, headers=self.headers, timeout=30,
            )
            if resp.status_code in (200, 201):
                logger.info(f" Agent registered successfully")
                return True
            else:
                logger.error(f"Registration failed: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def heartbeat(self, agent_id: str) -> bool:
        try:
            resp = requests.post(
                f"{self.backend_url}/api/assets/agent/heartbeat",
                json={"agent_id": agent_id, "status": "online"},
                headers=self.headers, timeout=10,
            )
            return resp.status_code == 200
        except:
            return False


def main():
    if not HAS_REQUESTS:
        logger.error("Missing 'requests' library. Install: pip install requests")
        sys.exit(1)

    logger.info(" SentinelX AI Agent starting...")
    
    collector = SystemCollector()
    client = AgentClient(BACKEND_URL, AGENT_TOKEN)

    # Initial registration with full inventory
    logger.info(" Collecting system inventory...")
    data = collector.collect_all()
    logger.info(f"  OS: {data['os_name']} {data['os_version']}")
    logger.info(f"  IP: {data['ip_address']}")
    logger.info(f"  Software: {len(data['installed_software'])} packages")
    logger.info(f"  Services: {len(data['running_services'])} listening")
    logger.info(f"  Ports: {data['open_ports']}")

    client.register(data)

    # Heartbeat loop
    logger.info(f" Starting heartbeat (every {HEARTBEAT_INTERVAL}s)")
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        if client.heartbeat(collector.agent_id):
            logger.debug("Heartbeat sent")
        else:
            logger.warning("Heartbeat failed, attempting re-registration")
            data = collector.collect_all()
            client.register(data)


if __name__ == "__main__":
    main()
