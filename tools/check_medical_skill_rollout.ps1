param(
    [string]$ReportPath,
    [string]$TaskName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$workspace = 'D:\汇度编辑部1\写作知识库'
$schemePath = Join-Path $workspace 'medical_kb_system_v2\docs\医学写作Skill封装方案_20260311.md'
$reportDir = Join-Path $workspace '写作项目运行日志'
$liveSkillRoot = 'C:\Users\96138\.config\opencode\skills'

$targetFiles = [ordered]@{
    'scheme' = $schemePath
    'router' = Join-Path $liveSkillRoot 'medical-content-router\SKILL.md'
    'writing' = Join-Path $liveSkillRoot 'medical-writing\SKILL.md'
    'opinion' = Join-Path $liveSkillRoot 'medical-opinion-generator\SKILL.md'
    'review' = Join-Path $liveSkillRoot 'medical-article-reviewer\SKILL.md'
    'query' = Join-Path $liveSkillRoot 'medical-database-query\SKILL.md'
}

if (-not $ReportPath) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $ReportPath = Join-Path $reportDir ("medical_skill_rollout_check_{0}.md" -f $timestamp)
}

$results = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details
    )

    $results.Add([pscustomobject]@{
        Name = $Name
        Passed = $Passed
        Details = $Details
    })
}

function Read-Text {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    return Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
}

foreach ($entry in $targetFiles.GetEnumerator()) {
    $exists = Test-Path -LiteralPath $entry.Value
    $length = if ($exists) { (Get-Item -LiteralPath $entry.Value).Length } else { 0 }
    Add-Check -Name ("文件存在: {0}" -f $entry.Key) -Passed ($exists -and $length -gt 0) -Details ("{0} | size={1}" -f $entry.Value, $length)
}

$routerText = Read-Text $targetFiles['router']
$writingText = Read-Text $targetFiles['writing']
$opinionText = Read-Text $targetFiles['opinion']
$reviewText = Read-Text $targetFiles['review']
$queryText = Read-Text $targetFiles['query']
$combinedTexts = @($routerText, $writingText, $opinionText, $reviewText, $queryText) -join "`n"

$requiredWritingTokens = @(
    'medical-content-router',
    'source_packet',
    'prototype_hint',
    'target_audience',
    'rewrite_target'
)
$missingWritingTokens = @($requiredWritingTokens | Where-Object { $writingText -notmatch [regex]::Escape($_) })
Add-Check `
    -Name 'medical-writing 已写入显式直写阈值' `
    -Passed ($null -ne $writingText -and $missingWritingTokens.Count -eq 0) `
    -Details ($(if ($missingWritingTokens.Count -eq 0) { 'required tokens found' } else { 'missing: ' + ($missingWritingTokens -join ', ') }))

$legacyWritingPhrases = @(
    '观点+写作+审核',
    '完整链路',
    '生成医学内容',
    '检查合规性',
    '查一下这个病的知识',
    '帮我审核这篇文章',
    '从这些证据形成观点'
)
$presentLegacyWritingPhrases = @($legacyWritingPhrases | Where-Object { $writingText -match [regex]::Escape($_) })
Add-Check `
    -Name 'medical-writing 旧广义组合触发已收缩' `
    -Passed ($null -ne $writingText -and $presentLegacyWritingPhrases.Count -eq 0) `
    -Details ($(if ($presentLegacyWritingPhrases.Count -eq 0) { 'no legacy trigger phrases found' } else { 'still present: ' + ($presentLegacyWritingPhrases -join ', ') }))

$childRedirectChecks = @(
    @{ Name = 'medical-opinion-generator'; Text = $opinionText },
    @{ Name = 'medical-article-reviewer'; Text = $reviewText },
    @{ Name = 'medical-database-query'; Text = $queryText }
)

$childRedirectFailures = [System.Collections.Generic.List[string]]::new()
foreach ($check in $childRedirectChecks) {
    $hasRouterRedirect = $check.Text -match 'medical-content-router'
    $stillRedirectsToWriting = $check.Text -match '请调用 `medical-writing`'
    if (-not $hasRouterRedirect -or $stillRedirectsToWriting) {
        $childRedirectFailures.Add($check.Name)
    }
}
Add-Check `
    -Name '三个子模块的组合请求 redirect 已切到 router' `
    -Passed ($childRedirectFailures.Count -eq 0) `
    -Details ($(if ($childRedirectFailures.Count -eq 0) { 'all child skills redirect to medical-content-router' } else { 'needs update: ' + ($childRedirectFailures -join ', ') }))

$residualBackflowMatches = [System.Collections.Generic.List[string]]::new()
foreach ($check in $childRedirectChecks) {
    if ($check.Text -match '请调用 `medical-writing`') {
        $residualBackflowMatches.Add($check.Name)
    }
}
Add-Check `
    -Name '不存在子模块把组合请求导回 medical-writing 的残留说明' `
    -Passed ($residualBackflowMatches.Count -eq 0) `
    -Details ($(if ($residualBackflowMatches.Count -eq 0) { 'no residual child backflow found' } else { 'residual backflow in: ' + ($residualBackflowMatches -join ', ') }))

$handoffTokens = @(
    'query_to_write',
    'opinion_to_write',
    'review_then_rewrite',
    'planning_to_write',
    'control_context',
    'log_context'
)
$missingHandoffTokens = @($handoffTokens | Where-Object { $combinedTexts -notmatch [regex]::Escape($_) })
Add-Check `
    -Name '单次握手与最小 handoff 契约已写入 live skill' `
    -Passed ($missingHandoffTokens.Count -eq 0) `
    -Details ($(if ($missingHandoffTokens.Count -eq 0) { 'handoff and context tokens found' } else { 'missing: ' + ($missingHandoffTokens -join ', ') }))

$failedChecks = @($results | Where-Object { -not $_.Passed })
$allPassed = $failedChecks.Count -eq 0
$overallStatus = if ($allPassed) { '已验证' } else { '未验证' }
$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'

$reportLines = [System.Collections.Generic.List[string]]::new()
$reportLines.Add('# 医学写作 Skill 封装方案执行结果自动检查报告')
$reportLines.Add('')
$reportLines.Add(('> **检查对象**: `{0}`' -f $schemePath))
$reportLines.Add(('> **生成时间**: `{0}`' -f $now))
$reportLines.Add(('> **状态**: `{0}`' -f $overallStatus))
$reportLines.Add('')
$reportLines.Add('---')
$reportLines.Add('')
$reportLines.Add('## 检查结果')
$reportLines.Add('')

foreach ($result in $results) {
    $prefix = if ($result.Passed) { '[通过]' } else { '[未通过]' }
    $reportLines.Add(('- {0} {1}: {2}' -f $prefix, $result.Name, $result.Details))
}

$reportLines.Add('')
$reportLines.Add('## 结论')
$reportLines.Add('')
if ($allPassed) {
    $reportLines.Add('- 已验证：当前 live skill 文件已满足本轮《医学写作Skill封装方案_20260311.md》要求的入口唯一化、子模块 redirect 迁移、显式直写阈值、单次握手与最小 handoff 契约。')
} else {
    $reportLines.Add('- 未验证：仍有检查项未通过，不能宣称《医学写作Skill封装方案_20260311.md》已完成落地。')
    $reportLines.Add('- 当前报告只基于文件直接核对，不替代人工复核实际运行链路。')
}

$reportLines.Add('')
$reportLines.Add('## Evidence Summary')
$reportLines.Add('')
$evidenceFiles = '- 直接核对了方案文件与 5 个 live skill 文件：`{0}`、`{1}`、`{2}`、`{3}`、`{4}`、`{5}`。' -f `
    $schemePath, $targetFiles['router'], $targetFiles['writing'], $targetFiles['opinion'], $targetFiles['review'], $targetFiles['query']
$evidenceRedirect = '- 直接检索了子模块中是否仍存在 `请调用 `medical-writing`` 这类回流说明；结果：`{0}`。' -f `
    $(if ($residualBackflowMatches.Count -eq 0) { '未发现残留' } else { $residualBackflowMatches -join ', ' })
$evidenceThreshold = '- 直接检查了 `medical-writing` 的显式直写阈值与 handoff 关键字段；缺失项：`{0}`。' -f `
    $(if (($missingWritingTokens.Count + $missingHandoffTokens.Count) -eq 0) { '无' } else { (@($missingWritingTokens + $missingHandoffTokens) -join ', ') })
$reportLines.Add($evidenceFiles)
$reportLines.Add($evidenceRedirect)
$reportLines.Add($evidenceThreshold)

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($ReportPath, $reportLines, $utf8NoBom)

if ($TaskName) {
    try {
        schtasks /Delete /TN $TaskName /F | Out-Null
    } catch {
        # Ignore self-delete failures and keep the report.
    }
}

Write-Output $ReportPath
