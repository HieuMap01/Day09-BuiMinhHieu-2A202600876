$Ports = @(10000, 10100, 10101, 10102, 10103)

foreach ($Port in $Ports) {
    $Connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($Connection in $Connections) {
        if ($Connection.OwningProcess) {
            $Process = Get-Process -Id $Connection.OwningProcess -ErrorAction SilentlyContinue
            if ($Process) {
                Write-Host "Stopping $($Process.ProcessName) on port $Port (PID $($Process.Id))"
                Stop-Process -Id $Process.Id -Force
            }
        }
    }
}
