$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv')) { py -3.11 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
if (-not (Test-Path 'harness.toml')) { Copy-Item harness.example.toml harness.toml }
Write-Host 'XenonHarness bootstrap complete.'
Write-Host 'Edit harness.toml, then run: .\.venv\Scripts\xenonharness.exe doctor'
