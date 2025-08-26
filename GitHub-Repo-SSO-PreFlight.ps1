# GitHub Repo & SSO Pre-Flight Check
# ASCII only, PowerShell 5.1 compatible

# Parameters
param(
    # Repository in format: owner/repo
    [string]$Repo = "mszewczy/moje-narzedzia-ai-1967",

    # Organization name for SSO validation
    [string]$OrgName = "PC24 Marek SZEWCZYK",

    # Full path to the public SSH key
    [string]$KeyPublicPath = "$env:USERPROFILE\.ssh\id_ed25519.pub",

    # Full path to the private SSH key
    [string]$KeyPrivatePath = "$env:USERPROFILE\.ssh\id_ed25519",

    # MODIFIED: Updated log file name prefix
    [string]$LogFile = ".\logs\WINDOWS-PreFlight_{0}.log" -f (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
)

# Array to hold summary messages for final output
$Summary = @()

# Function to write log messages to console and file
function Write-Log {
    param(
        [string]$Level,
        [string]$Message,
        [string]$Color="White"
    )
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[{0}] [{1}] {2}" -f $timestamp, $Level, $Message
    
    # Write to console with color
    Write-Host $line -ForegroundColor $Color
    
    # Write to log file
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    
    # Add key statuses to the summary
    if ($Level -in @("OK", "WARN", "ERROR")) {
        $Summary += "{0,-40} : {1}" -f $Message, $Level
    }
}

# Helper functions for different log levels
function Info { param([string]$m) Write-Log "INFO"  $m "Cyan" }
function Ok   { param([string]$m) Write-Log "OK"    $m "Green" }
function Warn { param([string]$m) Write-Log "WARN"  $m "Yellow" }
function Fail { param([string]$m) Write-Log "ERROR" $m "Red" }

# --- SCRIPT EXECUTION STARTS HERE ---

# -1) Clean up old logs
Info "Cleaning up logs older than 7 days..."
$scriptPath = $PSScriptRoot | Split-Path -Parent
Get-ChildItem -Path $scriptPath -Filter "WINDOWS-PreFlight_*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item
Ok "Log cleanup complete."

# 0) Configure SSH Agent (Crucial for Windows)
Info "Configuring SSH Agent..."
try {
    $agent = Get-Service ssh-agent -ErrorAction Stop
    if ($agent.Status -ne "Running") {
        Info "SSH Agent service is not running. Attempting to start it..."
        Set-Service -Name ssh-agent -StartupType 'Automatic' -ErrorAction Stop
        Start-Service ssh-agent -ErrorAction Stop
        Info "SSH Agent service started."
    }
    
    $escapedPath = [regex]::Escape($KeyPrivatePath)
    $identities = ssh-add -l 2>$null
    
    if (-not ($identities -match $escapedPath)) {
        Info "Adding SSH key to the agent..."
        $addResult = ssh-add $KeyPrivatePath 2>&1
        if ($LASTEXITCODE -ne 0) {
            Add-Content -Path $LogFile -Value "SSH_ADD_ERROR: $addResult"
            Warn "Could not add SSH key to the agent. Error: $addResult"
        } else {
            Ok "SSH key successfully added to the agent."
        }
    } else {
        Ok "SSH key is already present in the agent."
    }
} catch {
    $errorMessage = $_.Exception.Message
    Add-Content -Path $LogFile -Value "SSH_AGENT_SERVICE_ERROR: $errorMessage"
    Fail "Failed to configure the SSH Agent service. Error: $errorMessage"
    exit 1
}


# 1) Check for local SSH keys
Info "Checking local SSH keys..."
if (-not (Test-Path -LiteralPath $KeyPublicPath)) { Fail "Public key not found at: $KeyPublicPath"; exit 1 }
if (-not (Test-Path -LiteralPath $KeyPrivatePath)) { Fail "Private key not found at: $KeyPrivatePath"; exit 1 }
Ok "Local SSH keys found"

# 2) Check for GitHub CLI ('gh')
Info "Checking GitHub CLI..."
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) { Fail "GitHub CLI ('gh') command not found in PATH"; exit 1 }

# Check authentication status of GitHub CLI
$authStatus = & gh auth status 2>&1
Add-Content -Path $LogFile -Value "AUTH_STATUS: $authStatus"
if ($LASTEXITCODE -ne 0) { Fail "GitHub CLI is not authenticated. Run 'gh auth login'."; exit 1 }
Ok "GitHub CLI is available and authenticated"

# 3) Test SSH connectivity to GitHub
Info "Testing SSH connection to GitHub..."
$rawSshOutput = & ssh -T git@github.com 2>&1
$sshCleanOutput = $rawSshOutput -replace "Warning: Permanently added .*?known hosts\.\s*", ""
Add-Content -Path $LogFile -Value "SSH_TEST_RAW: $rawSshOutput"
if ($sshCleanOutput -match "successfully authenticated") {
    Ok "SSH connectivity to GitHub is successful"
} else {
    Fail "SSH connection failed: $sshCleanOutput"; exit 1
}

# 4) Check if the local SSH key is present on GitHub and authorized for the org
Info "Retrieving SSH keys from GitHub account..."
$keysJson = & gh api user/keys 2>&1
Add-Content -Path $LogFile -Value "SSH_KEYS_JSON_RAW: $keysJson"
if ($LASTEXITCODE -ne 0 -or -not $keysJson) { Fail "Could not retrieve SSH keys from GitHub"; exit 1 }

$keys = $keysJson | ConvertFrom-Json

# Robustly read and clean the local public key before comparison
$localPublicKeyContent = (Get-Content -LiteralPath $KeyPublicPath -Raw).Trim()
$localPublicKeyParts = $localPublicKeyContent -split '\s+'
$cleanedLocalPublicKey = "$($localPublicKeyParts[0]) $($localPublicKeyParts[1])"

$matchedKey = $keys | Where-Object { $_.key -eq $cleanedLocalPublicKey }

if (-not $matchedKey) { Fail "Local public key is not registered on your GitHub account"; exit 1 }
Ok ("SSH key found on GitHub with title: $($matchedKey.title)")

Ok ("Key authorization for org will be verified by repository access.")

# 5) Check repository access permissions
Info ("Checking repository access for: $Repo")
$repoJson = & gh repo view $Repo --json name,visibility,viewerPermission 2>&1
Add-Content -Path $LogFile -Value "REPO_JSON_RAW: $repoJson"
if ($LASTEXITCODE -ne 0 -or -not $repoJson) { Fail "Repository not found or you have no access. This may indicate an SSO issue."; exit 1 }

$repoObj = $repoJson | ConvertFrom-Json
Ok ("Repository visibility: $($repoObj.visibility)")
Ok ("Your permission level: $($repoObj.viewerPermission)")
if ($repoObj.viewerPermission -notin @("READ", "WRITE", "ADMIN")) { Fail "Insufficient permission to the repository"; exit 1 }
Ok ("Successfully accessed org repository, SSO authorization confirmed.")

# Define the correct path to ssh.exe to be used by git
$SshExePath = "$env:SystemRoot\System32\OpenSSH\ssh.exe"

# 6) Validate git operations using SSH
Info "Validating git ls-remote via SSH..."
# MODIFIED BLOCK: Explicitly tell git which ssh.exe to use to bypass configuration issues.
$gitErrorOutput = ""
& git -c "core.sshCommand=$SshExePath" ls-remote ("git@github.com:" + $Repo) 2>&1 | ForEach-Object { $gitErrorOutput += $_ }

if ($LASTEXITCODE -ne 0) {
    Add-Content -Path $LogFile -Value "GIT_LS_REMOTE_ERROR: $gitErrorOutput"
    Fail "git ls-remote via SSH failed. See log for details."; exit 1
}
Ok "SSH access to repository confirmed with git"

# 7) Perform git fetch and pull
Info "Fetching latest changes from remote..."
# MODIFIED BLOCK: Explicitly tell git which ssh.exe to use.
$fetchOutput = & git -c "core.sshCommand=$SshExePath" fetch --all 2>&1
$fetchOutput | Add-Content -Path $LogFile
if ($LASTEXITCODE -ne 0) {
    Fail "git fetch failed"
    exit 1
}
Ok "Fetch completed successfully"

Info "Pulling latest changes..."
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($LASTEXITCODE -ne 0) {
    Fail "Could not determine the current git branch."
    exit 1
}
Info "Current branch is '$currentBranch'. Pulling from origin..."
# MODIFIED BLOCK: Explicitly tell git which ssh.exe to use.
$pullOutput = & git -c "core.sshCommand=$SshExePath" pull origin $currentBranch 2>&1
$pullOutput | Add-Content -Path $LogFile
if ($LASTEXITCODE -ne 0) {
    Fail "git pull failed"
    exit 1
}
Ok "Pull completed successfully"

# 8) Display final summary
Write-Host ""
Write-Host "=== PRE-FLIGHT CHECK SUMMARY ===" -ForegroundColor Magenta
Add-Content -Path $LogFile -Value "`n=== SUMMARY ==="
foreach ($line in $Summary) {
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Write-Host ""
Ok "All pre-flight checks passed and repository is up-to-date."
Write-Host "Full log saved to: $LogFile" -ForegroundColor Cyan
