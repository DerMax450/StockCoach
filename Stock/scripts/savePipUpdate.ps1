# Optional: Aktivierung des venv (anpassen!)
# & "C:\Pfad\zu\deinem\venv\Scripts\Activate.ps1"

Write-Host "🔍 Lade veraltete Pakete..."
$pipOutdated = pip3 list --outdated --format=json | ConvertFrom-Json

foreach ($pkg in $pipOutdated) {
    $name = $pkg.name
    $current = $pkg.version
    $latest = $pkg.latest_version

    # Optional: Sonderregeln für kritische Pakete
    if ($name -eq "numpy") {
        if ([version]$latest -ge [version]"2.2.0") {
            Write-Host "⚠️  Überspringe $name ($latest wäre inkompatibel mit TensorFlow 2.19)" -ForegroundColor Yellow
            continue
        }
    }

    if ($name -eq "protobuf") {
        if ([version]$latest -ge [version]"4.21.0") {
            Write-Host "⚠️  Überspringe $name ($latest entfernt GetPrototype)" -ForegroundColor Yellow
            continue
        }
    }

    Write-Host "⬆️  Aktualisiere $name von $current auf $latest..." -ForegroundColor Cyan
    pip3 install --upgrade $name
}

Write-Host "`n✅ Alle kompatiblen Pakete wurden aktualisiert."
