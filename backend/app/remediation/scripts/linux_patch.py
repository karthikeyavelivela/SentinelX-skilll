"""Linux patch script generator for apt, yum, and dnf."""


def generate_apt_patch(package_name: str, target_version: str = None, dry_run: bool = True) -> dict:
    """Generate apt-based patch script for Debian/Ubuntu."""
    
    if dry_run:
        script = f"""#!/bin/bash
set -euo pipefail

echo "=== VulnGuard AI - Dry Run Patch ==="
echo "Package: {package_name}"
echo "Target: {target_version or 'latest'}"
echo ""

echo "[DRY RUN] Checking package availability..."
apt-cache policy {package_name}

echo ""
echo "[DRY RUN] Simulating upgrade..."
apt-get install --dry-run -y {package_name}{'=' + target_version if target_version else ''}

echo ""
echo "[DRY RUN] Dependencies that would change:"
apt-get install --dry-run -y {package_name} 2>&1 | grep -E "^  |upgraded|newly installed"

echo ""
echo "=== Dry run complete. No changes made. ==="
"""
    else:
        script = f"""#!/bin/bash
set -euo pipefail

LOGFILE="/var/log/vulnguard/patch_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /var/log/vulnguard

echo "=== VulnGuard AI - Applying Patch ===" | tee -a "$LOGFILE"
echo "Date: $(date)" | tee -a "$LOGFILE"
echo "Package: {package_name}" | tee -a "$LOGFILE"
echo "Target: {target_version or 'latest'}" | tee -a "$LOGFILE"

# Record current state
CURRENT_VERSION=$(dpkg -l {package_name} 2>/dev/null | grep '^ii' | awk '{{print $3}}')
echo "Current version: $CURRENT_VERSION" | tee -a "$LOGFILE"

# Update package lists
apt-get update -qq 2>&1 | tee -a "$LOGFILE"

# Install/upgrade
apt-get install -y {package_name}{'=' + target_version if target_version else ''} 2>&1 | tee -a "$LOGFILE"

# Verify
NEW_VERSION=$(dpkg -l {package_name} 2>/dev/null | grep '^ii' | awk '{{print $3}}')
echo "New version: $NEW_VERSION" | tee -a "$LOGFILE"

echo "=== Patch applied successfully ===" | tee -a "$LOGFILE"
"""

    rollback = f"""#!/bin/bash
set -euo pipefail

echo "=== VulnGuard AI - Rollback ==="
echo "Rolling back {package_name} to previous version..."

# Try to downgrade to the previous version
apt-get install -y --allow-downgrades {package_name}=$CURRENT_VERSION

echo "=== Rollback complete ==="
"""

    return {"script": script, "rollback": rollback}


def generate_yum_patch(package_name: str, target_version: str = None, dry_run: bool = True) -> dict:
    """Generate yum/dnf-based patch script for RHEL/CentOS/Fedora."""
    
    pkg_manager = "dnf"
    
    if dry_run:
        script = f"""#!/bin/bash
set -euo pipefail

echo "=== VulnGuard AI - Dry Run Patch ==="
echo "Package: {package_name}"

echo "[DRY RUN] Current package info:"
{pkg_manager} info {package_name}

echo ""
echo "[DRY RUN] Available updates:"
{pkg_manager} check-update {package_name} || true

echo ""
echo "[DRY RUN] Simulating update..."
{pkg_manager} update --assumeno {package_name} || true

echo "=== Dry run complete. No changes made. ==="
"""
    else:
        script = f"""#!/bin/bash
set -euo pipefail

LOGFILE="/var/log/vulnguard/patch_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /var/log/vulnguard

echo "=== VulnGuard AI - Applying Patch ===" | tee -a "$LOGFILE"

CURRENT_VERSION=$({pkg_manager} list installed {package_name} 2>/dev/null | grep {package_name} | awk '{{print $2}}')
echo "Current version: $CURRENT_VERSION" | tee -a "$LOGFILE"

{pkg_manager} update -y {package_name} 2>&1 | tee -a "$LOGFILE"

NEW_VERSION=$({pkg_manager} list installed {package_name} 2>/dev/null | grep {package_name} | awk '{{print $2}}')
echo "New version: $NEW_VERSION" | tee -a "$LOGFILE"

echo "=== Patch applied successfully ===" | tee -a "$LOGFILE"
"""

    rollback = f"""#!/bin/bash
set -euo pipefail

echo "=== VulnGuard AI - Rollback ==="
{pkg_manager} history undo last -y
echo "=== Rollback complete ==="
"""

    return {"script": script, "rollback": rollback}
