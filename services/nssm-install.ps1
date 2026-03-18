# ================================
# NSSM Installation Script
# Automated Multi-Agent Incident System
# ================================

# -------- CONFIGURATION --------
$BaseDir = "C:\Users\tosim\incident-system"
$PythonExe = "C:\Users\tosim\AppData\Local\Programs\Python\Python311\python.exe"
$NssmExe = "C:\nssm\nssm.exe"

$Services = @(
    @{
        Name = "MCPServer"
        Args = "-m uvicorn mcp_server.server:app --host 127.0.0.1 --port 8000 --loop asyncio --http h11 --lifespan off --workers 1"
        LogOut = "$BaseDir\logs\mcp_stdout.log"
        LogErr = "$BaseDir\logs\mcp_stderr.log"
    },
    @{
        Name = "SlackTicketAgent"
        Args = "-m uvicorn agent_ticket.slack_ticket_agent:app --host 127.0.0.1 --port 9000 --loop asyncio --http h11 --lifespan off --workers 1"
        LogOut = "$BaseDir\logs\slack_stdout.log"
        LogErr = "$BaseDir\logs\slack_stderr.log"
    },
    @{
        Name = "LogAgent"
        Args = "$BaseDir\agent_logs\log_agent.py"
        LogOut = "$BaseDir\logs\log_stdout.log"
        LogErr = "$BaseDir\logs\log_stderr.log"
    }
)

# -------- SAFETY CHECKS --------
if (-not (Test-Path $NssmExe)) {
    Write-Error "NSSM not found at $NssmExe"
    exit 1
}

if (-not (Test-Path $PythonExe)) {
    Write-Error "Python not found at $PythonExe"
    exit 1
}

New-Item -ItemType Directory -Force -Path "$BaseDir\logs" | Out-Null

# -------- INSTALL SERVICES --------
foreach ($svc in $Services) {

    Write-Host "Installing service $($svc.Name)..."

    & $NssmExe install $svc.Name $PythonExe $svc.Args
    & $NssmExe set $svc.Name AppDirectory $BaseDir

    & $NssmExe set $svc.Name AppStdout $svc.LogOut
    & $NssmExe set $svc.Name AppStderr $svc.LogErr

    & $NssmExe set $svc.Name AppRestartDelay 5000
    & $NssmExe set $svc.Name Start SERVICE_AUTO_START

    & $NssmExe set $svc.Name AppEnvironmentExtra `
        "PYTHONUNBUFFERED=1"

    Write-Host "Service $($svc.Name) installed successfully."
}

Write-Host "All services installed."
Write-Host "Use 'nssm start <ServiceName>' to start them."
