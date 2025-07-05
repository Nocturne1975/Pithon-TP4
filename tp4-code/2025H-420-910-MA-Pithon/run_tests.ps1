$env:PYTHONPATH="$PSScriptRoot\src"
pytest -q --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Des tests ont échoué." -ForegroundColor Red
} else {
    Write-Host "✅ Tous les tests ont réussi !" -ForegroundColor Green
}
