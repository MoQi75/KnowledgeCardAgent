[CmdletBinding()]
param(
    [int]$BackendPort = 8080,
    [int]$FrontendPort = 3001,
    [switch]$Restart,
    [switch]$Install,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$FrontendRoot = Join-Path $RepoRoot "frontend"
$LogRoot = Join-Path $env:TEMP "KnowledgeCardAgent"
$BackendOut = Join-Path $LogRoot "backend.out.log"
$BackendErr = Join-Path $LogRoot "backend.err.log"
$FrontendOut = Join-Path $LogRoot "frontend.out.log"
$FrontendErr = Join-Path $LogRoot "frontend.err.log"
$StatusLog = Join-Path $LogRoot "startup-status.txt"

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Get-ChildProcessIds {
    param([int]$ParentId)

    $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentId }
    foreach ($child in $children) {
        Get-ChildProcessIds -ParentId $child.ProcessId
        $child.ProcessId
    }
}

function Stop-ProcessTree {
    param([int]$ProcessId)

    $ids = @(Get-ChildProcessIds -ParentId $ProcessId) + $ProcessId
    foreach ($id in ($ids | Select-Object -Unique)) {
        Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
    }
}

function Stop-ProjectProcesses {
    $currentPid = $PID
    $processes = Get-CimInstance Win32_Process | Where-Object {
        $_.ProcessId -ne $currentPid -and
        $_.CommandLine -and
        (
            ($_.CommandLine -like "*$RepoRoot*" -and $_.CommandLine -like "*src/run_service.py*") -or
            ($_.CommandLine -like "*$RepoRoot*" -and $_.CommandLine -like "*next* dev*") -or
            ($_.CommandLine -like "*$RepoRoot*" -and $_.CommandLine -like "*frontend\\.next*")
        )
    }

    foreach ($process in $processes) {
        Stop-ProcessTree -ProcessId $process.ProcessId
    }

    $portOwners = Get-NetTCPConnection -LocalPort $BackendPort, $FrontendPort -ErrorAction SilentlyContinue |
        Where-Object { $_.State -in @("Listen", "Bound") } |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($owner in $portOwners) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$owner" -ErrorAction SilentlyContinue
        if ($process -and $process.ProcessId -ne $currentPid) {
            Stop-ProcessTree -ProcessId $process.ProcessId
        }
        elseif (-not $process) {
            Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
        }
    }
}

function Wait-Http {
    param(
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $response.StatusCode
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $deadline)

    throw "$Name did not become ready: $Url"
}

function Test-HttpReady {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

Assert-Command "uv"
Assert-Command "npm.cmd"

if ($Restart) {
    Stop-ProjectProcesses
    Start-Sleep -Seconds 2
}

if ($Install) {
    Push-Location $RepoRoot
    try {
        uv sync
    }
    finally {
        Pop-Location
    }

    Push-Location $FrontendRoot
    try {
        npm.cmd install
    }
    finally {
        Pop-Location
    }
}

Remove-Item -LiteralPath $BackendOut, $BackendErr, $FrontendOut, $FrontendErr -Force -ErrorAction SilentlyContinue

$env:DATABASE_TYPE = "sqlite"
$env:SQLITE_DB_PATH = "checkpoints.db"
$env:USE_FAKE_MODEL = "true"
$env:HOST = "0.0.0.0"
$env:PORT = [string]$BackendPort
$env:MODE = "local"
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:$BackendPort"

$backendUrl = "http://127.0.0.1:$BackendPort/health"
$frontendUrl = "http://127.0.0.1:$FrontendPort/dashboard/default"

$backend = $null
if (-not (Test-HttpReady -Url $backendUrl)) {
    $backend = Start-Process `
        -FilePath (Get-Command "uv").Source `
        -ArgumentList @("run", "python", "src/run_service.py") `
        -WorkingDirectory $RepoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $BackendOut `
        -RedirectStandardError $BackendErr `
        -PassThru
}

$frontend = $null
if (-not (Test-HttpReady -Url $frontendUrl)) {
    $frontend = Start-Process `
        -FilePath (Get-Command "npm.cmd").Source `
        -ArgumentList @("run", "dev", "--", "--hostname", "127.0.0.1", "--port", [string]$FrontendPort) `
        -WorkingDirectory $FrontendRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $FrontendOut `
        -RedirectStandardError $FrontendErr `
        -PassThru
}

$backendStatus = Wait-Http -Name "Backend" -Url $backendUrl -TimeoutSeconds 90
$frontendStatus = Wait-Http -Name "Frontend" -Url $frontendUrl -TimeoutSeconds 90

if ($backend -and $backend.HasExited) {
    throw "Backend process exited early. Check log: $BackendErr"
}

if ($frontend -and $frontend.HasExited) {
    throw "Frontend process exited early. Check log: $FrontendErr"
}

$backendPid = if ($backend) { [string]$backend.Id } else { "already running" }
$frontendPid = if ($frontend) { [string]$frontend.Id } else { "already running" }

$summary = @(
    "KnowledgeCardAgent started successfully."
    "Backend:  $backendUrl ($backendStatus)"
    "Frontend: $frontendUrl ($frontendStatus)"
    "Backend PID:  $backendPid"
    "Frontend PID: $frontendPid"
    "Logs:"
    "  $BackendOut"
    "  $BackendErr"
    "  $FrontendOut"
    "  $FrontendErr"
)

$summary | Set-Content -Encoding UTF8 -Path $StatusLog
$summary | ForEach-Object { [Console]::Out.WriteLine($_) }

if ($OpenBrowser) {
    Start-Process $frontendUrl | Out-Null
}
