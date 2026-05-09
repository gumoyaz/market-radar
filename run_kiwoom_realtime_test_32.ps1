$python32 = Join-Path $env:LocalAppData 'Programs\Python\Python311-32\python.exe'
if (-not (Test-Path -LiteralPath $python32)) {
    Write-Error "32-bit Python not found at $python32"
    exit 1
}

& $python32 "$PSScriptRoot\test_kiwoom_realtime.py"
