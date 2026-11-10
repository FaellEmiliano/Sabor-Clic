param(
    [switch]$Demo
)

$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "O comando falhou com codigo $LASTEXITCODE."
    }
}

Push-Location -LiteralPath $PSScriptRoot
try {
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    $checkVersion = 'import sys; sys.exit(sys.version_info < (3, 10))'
    if (-not (Test-Path -LiteralPath $projectPython)) {
        if (Get-Command py.exe -ErrorAction SilentlyContinue) {
            Invoke-Checked 'py.exe' @('-3', '-c', $checkVersion)
            Invoke-Checked 'py.exe' @('-3', '-m', 'venv', '.venv')
        } elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
            Invoke-Checked 'python.exe' @('-c', $checkVersion)
            Invoke-Checked 'python.exe' @('-m', 'venv', '.venv')
        } else {
            throw 'Instale Python 3.10 ou superior e abra um novo PowerShell.'
        }
    }
    Invoke-Checked $projectPython @('-c', $checkVersion)
    Invoke-Checked $projectPython @('-m', 'pip', 'install', '-r', 'requirements.txt')

    if (-not (Test-Path -LiteralPath '.env')) {
        $sessionSecret = & $projectPython -c 'import secrets; print(secrets.token_hex(32))'
        if ($LASTEXITCODE -ne 0) {
            throw 'Falha ao gerar a chave da sessao.'
        }
        (Get-Content -LiteralPath '.env.example') -replace '^SECRET_KEY=.*$', "SECRET_KEY=$sessionSecret" |
            Set-Content -LiteralPath '.env' -Encoding ASCII
        Write-Host 'Preencha e salve o .env com os dados de um esquema MySQL ja criado.'
        Start-Process -FilePath 'notepad.exe' -ArgumentList '.env'
        [void](Read-Host 'Pressione Enter apos salvar o .env')
    }

    Set-Location -LiteralPath 'backend'
    $initArguments = @('-m', 'flask', '--app', 'run', 'init-db')
    if ($Demo) {
        $initArguments += '--demo'
    }
    Invoke-Checked $projectPython $initArguments

    Write-Host 'Instalacao concluida.'
    if (-not $Demo) {
        Write-Host 'Se precisar do primeiro administrador, execute dentro de backend:'
        Write-Host '..\.venv\Scripts\python.exe -m flask --app run create-admin'
    }
    Write-Host 'Para iniciar o sistema, execute dentro de backend:'
    Write-Host '..\.venv\Scripts\python.exe run.py'
} finally {
    Pop-Location
}
