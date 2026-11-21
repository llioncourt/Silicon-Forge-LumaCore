# Silicon Forge LumaCore | UVtools portable integration
# Windows PowerShell 5.1+. No global package install; all working files stay in repository.
# Notes: UVtools itself can maintain user preferences according to upstream behavior.
[CmdletBinding()]
param(
    [ValidateSet('install','gui','inspect','issues','compare','version','help')]
    [string]$Action = 'gui',
    [string]$InputFile = '',
    [string]$OtherFile = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Runtime = Join-Path $RepoRoot 'runtime'
$Version = '7.1.2'
$ExpectedSha256 = '8ed807737242738c8772c966f8bd302a214764e439e1e24893fbf9b65a542f41'
$ZipName = 'UVtools_win-x64_v7.1.2.zip'
$ZipUrl = 'https://github.com/sn4k3/UVtools/releases/download/v7.1.2/UVtools_win-x64_v7.1.2.zip'
$CacheDir = Join-Path $Runtime 'uvtools\downloads'
$InstallDir = Join-Path $Runtime "uvtools\v$Version"
$LogsDir = Join-Path $Runtime 'logs\uvtools'
$TempDir = Join-Path $Runtime 'tmp\uvtools'
$UserDir = Join-Path $Runtime 'user\uvtools'

function Ensure-Dirs {
    foreach ($dir in @($Runtime, $CacheDir, $LogsDir, $TempDir, $UserDir)) {
        if (-not (Test-Path -LiteralPath $dir -PathType Container)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
}

function Write-Log([string]$message) {
    $line = "[$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'))] $message"
    Write-Host $line
    Add-Content -LiteralPath (Join-Path $LogsDir 'bridge.log') -Value $line -Encoding UTF8
}

function Assert-Hash([string]$path) {
    $observed = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($observed -ne $ExpectedSha256) {
        throw "UVtools ZIP com checksum incorreto: $observed (esperado $ExpectedSha256). Nao foi instalado."
    }
}

function Find-Executable([string]$name) {
    if (-not (Test-Path -LiteralPath $InstallDir -PathType Container)) { return $null }
    $candidates = @(Get-ChildItem -LiteralPath $InstallDir -Filter $name -File -Recurse -ErrorAction SilentlyContinue)
    if ($candidates.Count -eq 0) { return $null }
    return $candidates[0].FullName
}

function Install-UVtools {
    Ensure-Dirs
    $existing = Find-Executable 'UVtools.exe'
    if ($existing) {
        Write-Log "UVtools v$Version encontrado em $existing"
        return
    }
    $zipPath = Join-Path $CacheDir $ZipName
    if (Test-Path -LiteralPath $zipPath -PathType Leaf) {
        try { Assert-Hash $zipPath } catch {
            Remove-Item -LiteralPath $zipPath -Force
            Write-Log 'Cache ZIP com hash incorreto foi descartado.'
        }
    }
    if (-not (Test-Path -LiteralPath $zipPath -PathType Leaf)) {
        $partPath = "$zipPath.part"
        if (Test-Path -LiteralPath $partPath) { Remove-Item -LiteralPath $partPath -Force }
        Write-Log "Baixando $ZipUrl"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $ZipUrl -UseBasicParsing -OutFile $partPath -MaximumRedirection 10
            Assert-Hash $partPath
            Move-Item -LiteralPath $partPath -Destination $zipPath
        } finally {
            if (Test-Path -LiteralPath $partPath) { Remove-Item -LiteralPath $partPath -Force }
        }
    } else { Assert-Hash $zipPath }
    Write-Log 'SHA-256 do ZIP oficial conferido.'
    $stage = Join-Path $TempDir ("extract-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    try {
        Expand-Archive -LiteralPath $zipPath -DestinationPath $stage -Force
        $exe = @(Get-ChildItem -LiteralPath $stage -Filter 'UVtools.exe' -Recurse -File)
        if ($exe.Count -ne 1) { throw "ZIP inesperado: $($exe.Count) executaveis UVtools.exe encontrados." }
        $sourceFolder = Split-Path -Parent $exe[0].FullName
        if (Test-Path -LiteralPath $InstallDir) {
            throw "Instalacao parcial em $InstallDir. Nao sobrescrevi; verifique a pasta."
        }
        Move-Item -LiteralPath $sourceFolder -Destination $InstallDir
        if (-not (Find-Executable 'UVtools.exe')) { throw 'UVtools.exe ausente apos a extracao.' }
        Write-Log "UVtools instalado em $InstallDir"
    } finally {
        if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    }
}

function Local-Environment {
    # Scoped to this PowerShell process and the child UVtools; does not change Windows registry.
    $env:UVTOOLS_LUMACORE_RUNTIME = $Runtime
    $env:DOTNET_BUNDLE_EXTRACT_BASE_DIR = Join-Path $TempDir 'dotnet'
    $env:DOTNET_CLI_HOME = Join-Path $UserDir 'dotnet'
    $env:TEMP = $TempDir
    $env:TMP = $TempDir
    $env:APPDATA = Join-Path $UserDir 'roaming'
    $env:LOCALAPPDATA = Join-Path $UserDir 'local'
    foreach ($p in @($env:DOTNET_BUNDLE_EXTRACT_BASE_DIR,$env:DOTNET_CLI_HOME,$env:APPDATA,$env:LOCALAPPDATA)) {
        if (-not (Test-Path -LiteralPath $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    }
}

function Resolve-Input([string]$file) {
    if ([string]::IsNullOrWhiteSpace($file)) { throw 'Informe o caminho do .pwsz (arraste para o BAT).' }
    $resolved = (Resolve-Path -LiteralPath $file -ErrorAction Stop).Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw "Arquivo inexistente: $file" }
    if ([IO.Path]::GetExtension($resolved).ToLowerInvariant() -ne '.pwsz') {
        throw "Somente arquivos .pwsz nesta integracao: $resolved"
    }
    return $resolved
}

function Execute-UVtools([string[]]$arguments, [string]$label) {
    $cmd = Find-Executable 'UVtoolsCmd.exe'
    $fallback = $false
    if (-not $cmd) {
        $cmd = Find-Executable 'UVtools.exe'
        $fallback = $true
    }
    if (-not $cmd) { throw 'Executavel UVtools nao encontrado apos instalacao.' }
    $args = @()
    if ($fallback) { $args += '--cmd' }
    $args += $arguments
    $logName = "$([DateTime]::Now.ToString('yyyyMMdd_HHmmss_fff'))_$label.log"
    $logPath = Join-Path $LogsDir $logName
    Write-Log "Executando UVtools: $label -> $logPath"
    Push-Location (Split-Path -Parent $cmd)
    try {
        & $cmd @args 2>&1 | Out-File -LiteralPath $logPath -Encoding UTF8
        $exitCode = $LASTEXITCODE
    } finally { Pop-Location }
    if ($exitCode -ne 0) {
        Write-Log "UVtools retornou erro $exitCode em $label; consulte o log."
        throw "Comando UVtools $label falhou, exit code $exitCode. Log: $logPath"
    }
    Write-Log "Executado: $label"
    return $logPath
}

function Hash-File([string]$file) {
    return (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Audit-File([string]$file, [bool]$withIssues) {
    $file = Resolve-Input $file
    $originalHash = Hash-File $file
    $report = @()
    $report += Execute-UVtools @('print-properties',$file) 'properties'
    if ($withIssues) { $report += Execute-UVtools @('print-issues',$file) 'issues' }
    if ($originalHash -ne (Hash-File $file)) { throw 'ALERTA: arquivo original foi alterado durante auditoria!' }
    Write-Log "Arquivo original intacto. SHA-256: $originalHash"
    Write-Host "Logs: $($report -join '; ')"
}

try {
    Ensure-Dirs
    if ($Action -eq 'help') {
        Write-Host 'Uso: UVTOOLS_GUI.bat [arquivo.pwsz] | AUDITAR_PWSZ.bat arquivo.pwsz'
        Write-Host 'PowerShell: uvtools.ps1 -Action install|gui|inspect|issues|compare|version'
        exit 0
    }
    Install-UVtools
    Local-Environment
    switch ($Action) {
        'install' { Write-Log "Instalacao validada em $InstallDir"; break }
        'gui' {
            $exe = Find-Executable 'UVtools.exe'
            $args = @()
            if ($InputFile) { $args = @('"' + (Resolve-Input $InputFile) + '"') }
            Write-Log 'Abrindo UVtools GUI.'
            if ($args.Count -gt 0) {
                Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe) -ArgumentList $args | Out-Null
            } else {
                Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe) | Out-Null
            }
            break
        }
        'inspect' { Audit-File $InputFile $false; break }
        'issues'  { Audit-File $InputFile $true; break }
        'compare' {
            $a = Resolve-Input $InputFile
            $b = Resolve-Input $OtherFile
            $hashA=Hash-File $a; $hashB=Hash-File $b
            $log=Execute-UVtools @('compare',$a,$b) 'compare'
            if ((Hash-File $a) -ne $hashA -or (Hash-File $b) -ne $hashB) {
                throw 'ALERTA: um arquivo foi alterado durante a comparacao!'
            }
            Write-Host "Comparacao registrada em $log"
            break
        }
        'version' {
            $log=Execute-UVtools @('--version') 'version'
            Get-Content -LiteralPath $log
            break
        }
    }
} catch {
    Write-Log ("FALHOU: " + $_.Exception.Message)
    Write-Error $_.Exception.Message
    exit 1
}
exit 0
