$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$Services = @(
    @{ Name = "registry"; Module = "registry"; Port = 10000; Delay = 2 },
    @{ Name = "tax_agent"; Module = "tax_agent"; Port = 10102; Delay = 2 },
    @{ Name = "compliance_agent"; Module = "compliance_agent"; Port = 10103; Delay = 2 },
    @{ Name = "law_agent"; Module = "law_agent"; Port = 10101; Delay = 3 },
    @{ Name = "customer_agent"; Module = "customer_agent"; Port = 10100; Delay = 3 }
)

Write-Host "Starting Legal Multi-Agent A2A services..."
Write-Host "Logs directory: $LogDir"

foreach ($Service in $Services) {
    $OutLog = Join-Path $LogDir "$($Service.Name).out.log"
    $ErrLog = Join-Path $LogDir "$($Service.Name).err.log"
    Write-Host "Starting $($Service.Name) on port $($Service.Port)..."
    Start-Process `
        -FilePath $Python `
        -ArgumentList "-m", $Service.Module `
        -WorkingDirectory $Root `
        -RedirectStandardOutput $OutLog `
        -RedirectStandardError $ErrLog `
        -WindowStyle Hidden
    Start-Sleep -Seconds $Service.Delay
}

Write-Host ""
Write-Host "All services started:"
Write-Host "  Registry:         http://localhost:10000"
Write-Host "  Customer Agent:   http://localhost:10100"
Write-Host "  Law Agent:        http://localhost:10101"
Write-Host "  Tax Agent:        http://localhost:10102"
Write-Host "  Compliance Agent: http://localhost:10103"
Write-Host ""
Write-Host "Run:"
Write-Host "  python test_client.py"
Write-Host ""
Write-Host "To stop services:"
Write-Host "  .\stop_all.ps1"
