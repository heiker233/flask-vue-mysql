param(
    [switch]$InstallFrontend
)

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[start-dev] $Message" -ForegroundColor Cyan
}

function Require-Path {
    param(
        [string]$Path,
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Name not found: $Path"
    }
}

function Resolve-Python {
    param([string]$Root)

    $candidates = @(
        (Join-Path $Root 'backend\venv\Scripts\python.exe'),
        (Join-Path $Root 'venv\Scripts\python.exe'),
        (Join-Path $Root 'flaskvue-env\Scripts\python.exe')
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return $pyLauncher.Source
    }

    throw 'Python was not found. Install Python or create a virtual environment first.'
}

function Quote-ForPowerShell {
    param([string]$Value)
    return "'" + ($Value -replace "'", "''") + "'"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$backendDir = Join-Path $rootDir 'backend'
$frontendDir = Join-Path $rootDir 'frontend'

Require-Path $backendDir 'Backend directory'
Require-Path $frontendDir 'Frontend directory'
Require-Path (Join-Path $backendDir 'app.py') 'Backend entry file'
Require-Path (Join-Path $frontendDir 'package.json') 'Frontend package file'

$pythonExe = Resolve-Python $rootDir
$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCommand) {
    $npmCommand = Get-Command npm -ErrorAction SilentlyContinue
}
if (-not $npmCommand) {
    throw 'npm was not found. Install Node.js first.'
}

Write-Step "Project: $rootDir"
Write-Step "Python: $pythonExe"
Write-Step "npm: $($npmCommand.Source)"

if ($InstallFrontend -or -not (Test-Path -LiteralPath (Join-Path $frontendDir 'node_modules'))) {
    Write-Step 'Installing frontend dependencies...'
    Push-Location $frontendDir
    try {
        & $npmCommand.Source install
    }
    finally {
        Pop-Location
    }
}

$backendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'CRM Backend - Flask'
Set-Location -LiteralPath $(Quote-ForPowerShell $backendDir)
Write-Host 'Starting Flask backend on http://localhost:5000' -ForegroundColor Cyan
& $(Quote-ForPowerShell $pythonExe) app.py
Write-Host ''
Read-Host 'Backend stopped. Press Enter to close'
"@

$frontendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'CRM Frontend - Vite'
Set-Location -LiteralPath $(Quote-ForPowerShell $frontendDir)
Write-Host 'Starting Vue frontend on http://localhost:5173' -ForegroundColor Cyan
& $(Quote-ForPowerShell $npmCommand.Source) run dev
Write-Host ''
Read-Host 'Frontend stopped. Press Enter to close'
"@

$backendEncoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($backendCommand))
$frontendEncoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($frontendCommand))

Start-Process powershell -WindowStyle Normal -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-NoExit',
    '-EncodedCommand', $backendEncoded
)

Start-Sleep -Seconds 1

Start-Process powershell -WindowStyle Normal -ArgumentList @(
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-NoExit',
    '-EncodedCommand', $frontendEncoded
)

Write-Step 'Development servers are starting.'
Write-Host ''
Write-Host 'Backend:  http://localhost:5000'
Write-Host 'Frontend: http://localhost:5173'
Write-Host ''
Write-Host 'Close the two service windows, or press Ctrl+C inside them, to stop the servers.'
