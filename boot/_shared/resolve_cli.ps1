# boot/_shared/resolve_cli.ps1
# Robust CLI binary resolver. Some npm-installed CLIs (gemini, codex) are
# .ps1/.cmd shims under %APPDATA%\npm. Spawned PS windows inherit PATH from
# the parent but `& <name>` resolution can drop these shims when PATHEXT is
# normalized by fix_pathext.ps1 (which strips .PS1) AND no .cmd is found via
# PATH lookup -- which has been observed under Start-Process spawn chains.
#
# Use this AFTER fix_pathext.ps1 has been dot-sourced. Returns the absolute
# path to an executable shim, or $null if not found.
#
# Usage (from a boot script):
#   . "$PSScriptRoot\_shared\resolve_cli.ps1"
#   $bin = Resolve-CliBinary "gemini"
#   if (-not $bin) { Write-Error "gemini CLI not on PATH"; exit 1 }
#   & $bin @cliArgs $initialMsg

function Resolve-CliBinary {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )

    # Try Get-Command first (respects current PATH + PATHEXT)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) {
        # Prefer .cmd / .exe over .ps1 to avoid double-shell overhead
        $src = $cmd.Source
        if ($src -and (Test-Path $src)) {
            # If we got a .ps1 but a .cmd exists alongside it, use the .cmd
            if ($src -match '\.ps1$') {
                $cmdPath = [System.IO.Path]::ChangeExtension($src, '.cmd')
                if (Test-Path $cmdPath) { return $cmdPath }
            }
            return $src
        }
    }

    # Fallback: walk known npm shim locations
    $candidates = @(
        (Join-Path $env:APPDATA      "npm\$Name.cmd"),
        (Join-Path $env:APPDATA      "npm\$Name.ps1"),
        (Join-Path $env:APPDATA      "npm\$Name.exe"),
        (Join-Path $env:LOCALAPPDATA "npm\$Name.cmd"),
        (Join-Path $env:LOCALAPPDATA "Programs\$Name\$Name.exe")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) { return $c }
    }

    return $null
}
