param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$JsonInput
)

$ErrorActionPreference = "Stop"

function Get-JwtPayload {
    param([string]$Token)

    try {
        $parts = $Token.Split('.')
        if ($parts.Count -lt 2) { return $null }

        $payload = $parts[1].Replace('-', '+').Replace('_', '/')
        switch ($payload.Length % 4) {
            2 { $payload += '==' }
            3 { $payload += '=' }
        }

        $bytes = [Convert]::FromBase64String($payload)
        $json = [Text.Encoding]::UTF8.GetString($bytes)
        return ($json | ConvertFrom-Json -ErrorAction Stop)
    }
    catch {
        return $null
    }
}

function Test-TavilyToken {
    param([string]$Token)

    $payload = Get-JwtPayload -Token $Token
    if (-not $payload) { return $false }

    if ($payload.iss -ne "https://mcp.tavily.com/") {
        return $false
    }

    if ($payload.exp) {
        $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        if ([long]$now -ge [long]$payload.exp) {
            return $false
        }
    }

    return $true
}

function Get-McpToken {
    $authDir = Join-Path $HOME ".mcp-auth"
    if (-not (Test-Path $authDir)) {
        return $null
    }

    $tokenFiles = Get-ChildItem -Path $authDir -Recurse -Filter "*_tokens.json" -File -ErrorAction SilentlyContinue
    foreach ($file in $tokenFiles) {
        try {
            $obj = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json -ErrorAction Stop
            $token = [string]$obj.access_token
            if (-not [string]::IsNullOrWhiteSpace($token) -and (Test-TavilyToken -Token $token)) {
                return $token
            }
        }
        catch {
            continue
        }
    }

    return $null
}

function Get-KeyFromClaudeSettings {
    $settingsPath = Join-Path $HOME ".claude/settings.json"
    if (-not (Test-Path $settingsPath)) {
        return $null
    }

    try {
        $settings = Get-Content -Path $settingsPath -Raw | ConvertFrom-Json -ErrorAction Stop
        $key = [string]$settings.env.TAVILY_API_KEY
        if (-not [string]::IsNullOrWhiteSpace($key)) {
            return $key
        }
    }
    catch {
        return $null
    }

    return $null
}


if ([string]::IsNullOrWhiteSpace($JsonInput)) {
    Write-Host "Usage: .\scripts\search.ps1 '<json>'"
    Write-Host ""
    Write-Host "Required:"
    Write-Host "  query: string - Search query (keep under 400 chars)"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\scripts\search.ps1 '{\"query\": \"latest AI trends\", \"time_range\": \"week\"}'"
    exit 1
}

$apiKey = $env:TAVILY_API_KEY
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = Get-KeyFromClaudeSettings
}
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = Get-McpToken
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Error "Error: TAVILY_API_KEY is not set, ~/.claude/settings.json has no key, and no valid Tavily token was found in ~/.mcp-auth/."
    exit 1
}


try {
    $requestObj = $JsonInput | ConvertFrom-Json -ErrorAction Stop
}
catch {
    Write-Error "Error: Invalid JSON input"
    exit 1
}

if (-not $requestObj.query) {
    Write-Error "Error: 'query' field is required"
    exit 1
}

$headers = @{
    Authorization = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Method Post -Uri "https://api.tavily.com/search" -Headers $headers -Body $JsonInput
    $response | ConvertTo-Json -Depth 20
}
catch {
    $errorBody = $null
    try {
        if ($_.Exception.Response) {
            $stream = $_.Exception.Response.GetResponseStream()
            if ($stream) {
                $reader = New-Object System.IO.StreamReader($stream)
                $errorBody = $reader.ReadToEnd()
                $reader.Close()
            }
        }
    }
    catch {
        # ignore body parse errors
    }

    if ($errorBody) {
        Write-Error "Tavily API request failed: $errorBody"
    }
    else {
        Write-Error ("Tavily API request failed: " + $_.Exception.Message)
    }

    exit 1
}
