param(
    [string]$TaskName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'check_medical_skill_rollout.ps1'
$scriptText = Get-Content -Raw -Encoding UTF8 -LiteralPath $scriptPath
$scriptBlock = [scriptblock]::Create($scriptText)

& $scriptBlock -TaskName $TaskName
