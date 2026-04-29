<#
.SYNOPSIS
    WorkBuddy Experience Asset Sync Script
.DESCRIPTION
    .\sync.ps1 gather  - collect files from local paths into repo
    .\sync.ps1 scatter - distribute repo files to local paths
    .\sync.ps1 push    - gather + git commit + push
    .\sync.ps1 pull    - git pull + scatter
    .\sync.ps1 sync    - pull then push (full bidirectional sync)
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("gather","scatter","push","pull","sync")]
    [string]$Action = "sync"
)

$ErrorActionPreference = "Continue"
$RepoRoot = $PSScriptRoot

$WB = "$env:USERPROFILE\.workbuddy"

# --- A: Identity ---
$StaticMap = [ordered]@{
    "global\SOUL.md"                  = "$WB\SOUL.md"
    "global\IDENTITY.md"              = "$WB\IDENTITY.md"
    "global\USER.md"                  = "$WB\USER.md"
}

# --- B: Memory ---
$MemoryMap = [ordered]@{
    "global\memery"                   = "$WB\memery"
    "global\memory"                   = "$WB\memory"
}

# --- C: Skills (auto-scan, no manual list needed) ---
# Gather: scan local skills dir -> repo
# Scatter: scan repo skills dir -> local
$SkillsLocalDir = "$WB\skills"
$SkillsRepoDir  = Join-Path $RepoRoot "skills"

# --- D: Project-level knowledge (auto-scan) ---
# Scan these root dirs for projects containing .workbuddy/
# Home PC: change to your drive, e.g. @("D:\")
$ProjectScanRoots = @("G:\")
# Sub-dirs inside .workbuddy/ worth syncing
$ProjectSyncDirs = @("memory", "learning", "scripts")
$ProjectsRepoDir = Join-Path $RepoRoot "projects"

# --- E: Knowledge base ---
$KnowledgeMap = [ordered]@{
    "knowledge\game-design-kb"        = "G:\project_output\game-design-kb"
}

# Combined static map (A+B, E only; C and D are auto-scanned)
$SyncMap = [ordered]@{}
foreach ($m in @($StaticMap, $MemoryMap, $KnowledgeMap)) {
    foreach ($entry in $m.GetEnumerator()) {
        $SyncMap[$entry.Key] = $entry.Value
    }
}

# Helper: discover all projects with .workbuddy/ under scan roots
function Get-ProjectSyncItems {
    $items = [ordered]@{}
    foreach ($root in $ProjectScanRoots) {
        if (-not (Test-Path $root)) { continue }
        $dirs = Get-ChildItem $root -Directory -Depth 0
        foreach ($dir in $dirs) {
            $wbDir = Join-Path $dir.FullName ".workbuddy"
            if (-not (Test-Path $wbDir)) { continue }
            $projName = $dir.Name
            foreach ($sub in $ProjectSyncDirs) {
                $subPath = Join-Path $wbDir $sub
                if (Test-Path $subPath) {
                    $repoKey = "projects\$projName\$sub"
                    $items[$repoKey] = $subPath
                }
            }
        }
    }
    return $items
}

function Write-Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
}

function Copy-SyncItem($src, $dst) {
    if (-not (Test-Path $src)) {
        Write-Log "  SKIP (not found): $src"
        return
    }
    $parentDir = Split-Path $dst -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    if (Test-Path $src -PathType Container) {
        if (-not (Test-Path $dst)) {
            New-Item -ItemType Directory -Path $dst -Force | Out-Null
        }
        robocopy $src $dst /E /XO /NJH /NJS /NDL /NFL /NC /NS /NP /XD __pycache__ node_modules .git | Out-Null
        Write-Log "  DIR: $src"
    } else {
        $srcInfo = Get-Item $src
        if ((Test-Path $dst)) {
            $dstInfo = Get-Item $dst
            if ($srcInfo.LastWriteTime -le $dstInfo.LastWriteTime) {
                return
            }
        }
        Copy-Item -Path $src -Destination $dst -Force
        Write-Log "  FILE: $src"
    }
}

function Invoke-Gather {
    Write-Log "=== GATHER: local -> repo ==="

    # Static items (A+B+E)
    foreach ($entry in $SyncMap.GetEnumerator()) {
        $repoDst = Join-Path $RepoRoot $entry.Key
        $localSrc = $entry.Value
        Copy-SyncItem $localSrc $repoDst
    }

    # Auto-scan skills (C)
    Write-Log "--- Scanning skills ---"
    if (Test-Path $SkillsLocalDir) {
        $localSkills = Get-ChildItem $SkillsLocalDir -Directory
        $existingRepoSkills = @()
        if (Test-Path $SkillsRepoDir) {
            $existingRepoSkills = (Get-ChildItem $SkillsRepoDir -Directory).Name
        }
        foreach ($skill in $localSkills) {
            $repoDst = Join-Path $SkillsRepoDir $skill.Name
            if ($skill.Name -notin $existingRepoSkills) {
                Write-Log "  [NEW SKILL] $($skill.Name)"
            }
            Copy-SyncItem $skill.FullName $repoDst
        }
        Write-Log "  Total skills: $($localSkills.Count)"
    }

    # Auto-scan projects (D)
    Write-Log "--- Scanning projects ---"
    $projItems = Get-ProjectSyncItems
    $existingRepoProjects = @()
    if (Test-Path $ProjectsRepoDir) {
        $existingRepoProjects = (Get-ChildItem $ProjectsRepoDir -Directory).Name
    }
    foreach ($entry in $projItems.GetEnumerator()) {
        $repoDst = Join-Path $RepoRoot $entry.Key
        $projName = ($entry.Key -split '\\')[1]
        if ($projName -notin $existingRepoProjects) {
            Write-Log "  [NEW PROJECT] $projName"
            $existingRepoProjects += $projName
        }
        Copy-SyncItem $entry.Value $repoDst
    }
    Write-Log "  Total project dirs: $($projItems.Count)"

    Write-Log "=== GATHER done ==="
}

function Invoke-Scatter {
    Write-Log "=== SCATTER: repo -> local ==="

    # Static items (A+B+E)
    foreach ($entry in $SyncMap.GetEnumerator()) {
        $repoSrc = Join-Path $RepoRoot $entry.Key
        $localDst = $entry.Value
        Copy-SyncItem $repoSrc $localDst
    }

    # Auto-scan skills (C)
    Write-Log "--- Distributing skills ---"
    if (Test-Path $SkillsRepoDir) {
        $repoSkills = Get-ChildItem $SkillsRepoDir -Directory
        $existingLocalSkills = @()
        if (Test-Path $SkillsLocalDir) {
            $existingLocalSkills = (Get-ChildItem $SkillsLocalDir -Directory).Name
        }
        foreach ($skill in $repoSkills) {
            $localDst = Join-Path $SkillsLocalDir $skill.Name
            if ($skill.Name -notin $existingLocalSkills) {
                Write-Log "  [NEW SKILL] $($skill.Name)"
            }
            Copy-SyncItem $skill.FullName $localDst
        }
        Write-Log "  Total skills: $($repoSkills.Count)"
    }

    # Auto-scan projects (D) - scatter uses local scan roots to determine target paths
    Write-Log "--- Distributing projects ---"
    if (Test-Path $ProjectsRepoDir) {
        $repoProjects = Get-ChildItem $ProjectsRepoDir -Directory
        foreach ($proj in $repoProjects) {
            # Find matching local project root under scan roots
            $localProjRoot = $null
            foreach ($root in $ProjectScanRoots) {
                $candidate = Join-Path $root $proj.Name
                if (Test-Path $candidate) {
                    $localProjRoot = $candidate
                    break
                }
            }
            if (-not $localProjRoot) {
                # Project not found locally, create under first scan root
                $localProjRoot = Join-Path $ProjectScanRoots[0] $proj.Name
                Write-Log "  [NEW PROJECT] $($proj.Name) -> $localProjRoot"
            }
            $subDirs = Get-ChildItem $proj.FullName -Directory
            foreach ($sub in $subDirs) {
                $localDst = Join-Path $localProjRoot ".workbuddy\$($sub.Name)"
                Copy-SyncItem $sub.FullName $localDst
            }
        }
        Write-Log "  Total projects: $($repoProjects.Count)"
    }

    Write-Log "=== SCATTER done ==="
}

function Invoke-GitPush {
    Write-Log "=== GIT PUSH ==="
    Push-Location $RepoRoot
    try {
        git add -A 2>&1 | Out-Null
        $status = git status --porcelain
        if (-not $status) {
            Write-Log "  No changes, skip commit"
            return
        }
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $hostname = $env:COMPUTERNAME
        git commit -m "sync from $hostname at $timestamp" 2>&1 | Out-Null
        git push origin main 2>&1
        Write-Log "  Pushed to GitHub"
    } finally {
        Pop-Location
    }
}

function Invoke-GitPull {
    Write-Log "=== GIT PULL ==="
    Push-Location $RepoRoot
    try {
        $branchExists = git ls-remote --heads origin main 2>&1
        if ($branchExists) {
            git pull --rebase origin main 2>&1
            Write-Log "  Pulled latest"
        } else {
            Write-Log "  Remote branch not found, skip pull (first run)"
        }
    } finally {
        Pop-Location
    }
}

Write-Log "WorkBuddy Sync - Action: $Action"

switch ($Action) {
    "gather"  { Invoke-Gather }
    "scatter" { Invoke-Scatter }
    "push"    { Invoke-Gather; Invoke-GitPush }
    "pull"    { Invoke-GitPull; Invoke-Scatter }
    "sync"    { Invoke-GitPull; Invoke-Scatter; Invoke-Gather; Invoke-GitPush }
}

Write-Log "=== ALL DONE ==="
