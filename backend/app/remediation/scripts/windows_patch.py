"""Windows patch script generator using PowerShell."""


def generate_windows_patch(package_name: str, kb_id: str = None, dry_run: bool = True) -> dict:
    """Generate PowerShell-based patch script for Windows."""
    
    if dry_run:
        script = f"""# VulnGuard AI - Dry Run Windows Patch
# Package: {package_name}
# KB: {kb_id or 'N/A'}

Write-Host "=== VulnGuard AI - Dry Run Patch ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)"
Write-Host "Package: {package_name}"
Write-Host ""

# Check current status
Write-Host "[DRY RUN] Checking installed updates..." -ForegroundColor Yellow
Get-HotFix | Select-Object -Property HotFixID, Description, InstalledOn | Format-Table -AutoSize

Write-Host ""
Write-Host "[DRY RUN] Checking Windows Update..."
$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
$SearchResult = $UpdateSearcher.Search("IsInstalled=0")

Write-Host "Available updates: $($SearchResult.Updates.Count)"
foreach ($Update in $SearchResult.Updates) {{
    Write-Host "  - $($Update.Title)" -ForegroundColor Gray
}}

Write-Host ""
Write-Host "=== Dry run complete. No changes made. ===" -ForegroundColor Green
"""
    else:
        script = f"""# VulnGuard AI - Windows Patch Application
# Package: {package_name}
# KB: {kb_id or 'N/A'}

$LogPath = "C:\\VulnGuard\\Logs\\patch_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path "C:\\VulnGuard\\Logs" | Out-Null

function Write-Log {{
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Tee-Object -FilePath $LogPath -Append
}}

Write-Log "=== VulnGuard AI - Applying Patch ==="
Write-Log "Package: {package_name}"

# Record current state
$CurrentHotfixes = Get-HotFix | Select-Object HotFixID
Write-Log "Current hotfixes: $($CurrentHotfixes.Count)"

# Create Windows Update session
$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()

# Search for specific update
$SearchQuery = "IsInstalled=0"
$SearchResult = $UpdateSearcher.Search($SearchQuery)

$UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
foreach ($Update in $SearchResult.Updates) {{
    if ($Update.Title -match "{package_name}" -or $Update.Title -match "{kb_id or ''}") {{
        $UpdatesToInstall.Add($Update) | Out-Null
        Write-Log "Queued: $($Update.Title)"
    }}
}}

if ($UpdatesToInstall.Count -gt 0) {{
    Write-Log "Installing $($UpdatesToInstall.Count) updates..."
    $Downloader = $UpdateSession.CreateUpdateDownloader()
    $Downloader.Updates = $UpdatesToInstall
    $Downloader.Download() | Out-Null

    $Installer = $UpdateSession.CreateUpdateInstaller()
    $Installer.Updates = $UpdatesToInstall
    $Result = $Installer.Install()

    Write-Log "Installation result: $($Result.ResultCode)"
    Write-Log "Reboot required: $($Result.RebootRequired)"
}} else {{
    Write-Log "No matching updates found."
}}

Write-Log "=== Patch application complete ==="
"""

    rollback = f"""# VulnGuard AI - Windows Rollback Script
# Uninstalling: {package_name} / {kb_id or 'N/A'}

Write-Host "=== VulnGuard AI - Rollback ===" -ForegroundColor Red

{"wusa /uninstall /kb:" + kb_id.replace("KB", "") + " /quiet /norestart" if kb_id else "Write-Host 'Manual rollback required - no KB ID specified'"}

Write-Host "=== Rollback complete ==="
"""

    return {"script": script, "rollback": rollback}


def generate_wsus_patch(server_url: str, computer_group: str = None, dry_run: bool = True) -> dict:
    """Generate WSUS-based patch deployment script."""
    
    script = f"""# VulnGuard AI - WSUS Deployment
# Server: {server_url}

Write-Host "=== VulnGuard AI - WSUS Sync ===" -ForegroundColor Cyan

# Force Windows Update detection
Write-Host "Triggering WSUS detection cycle..."
wuauclt /detectnow /updatenow

# Check for updates
$UpdateSession = New-Object -ComObject Microsoft.Update.Session
$Searcher = $UpdateSession.CreateUpdateSearcher()
$Searcher.ServerSelection = 1  # WSUS

$Results = $Searcher.Search("IsInstalled=0")
Write-Host "Pending updates from WSUS: $($Results.Updates.Count)"

foreach ($Update in $Results.Updates) {{
    Write-Host "  [$($Update.MsrcSeverity)] $($Update.Title)"
}}

{"Write-Host 'DRY RUN - No installation performed'" if dry_run else "# Auto-approve and install would go here"}
"""

    return {"script": script, "rollback": "# WSUS rollback via Group Policy"}
