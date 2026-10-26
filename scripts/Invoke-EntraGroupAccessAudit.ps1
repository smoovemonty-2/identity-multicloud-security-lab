
#Requires -Version 7.0
#Requires -Modules Microsoft.Graph.Authentication, Microsoft.Graph.Groups

<#
.SYNOPSIS
    Audits direct Entra ID security group memberships.

.DESCRIPTION
    Compares actual direct user membership against a
    private JSON access baseline and exports CSV reports.

    Read-only. Does not modify Entra ID.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$BaselinePath,

    [string]$OutputDirectory = (
        Join-Path $HOME "entra-audit-reports"
    )
)

$ErrorActionPreference = "Stop"

function Assert-GraphSession {
    param([string]$ExpectedTenantId)

    $context = Get-MgContext

    if (-not $context) {
        throw "No Graph session. Run Connect-MgGraph first."
    }

    if ($context.AuthType -ne "Delegated") {
        throw "This lab requires delegated authentication."
    }

    if ($context.TenantId -ne $ExpectedTenantId) {
        throw "Graph session tenant does not match baseline."
    }

    foreach ($scope in @("User.Read.All", "Group.Read.All")) {
        if ($scope -notin $context.Scopes) {
            throw "Missing required Graph scope: $scope"
        }
    }

    Write-Host "Graph authentication validated."
}

function Get-GroupAudit {
    param(
        [Parameter(Mandatory)]
        [object]$Definition
    )

    $group = Get-MgGroup `
        -GroupId $Definition.groupId `
        -Property "Id,DisplayName" `
        -ErrorAction Stop

    if ($group.DisplayName -ne $Definition.displayName) {
        throw "Group name mismatch for ID $($Definition.groupId)"
    }

    $members = @(
        Get-MgGroupMemberAsUser `
            -GroupId $group.Id `
            -Property "Id,DisplayName,UserPrincipalName" `
            -All `
            -ErrorAction Stop
    )

    $approvedIds = @(
        $Definition.approvedUserIds |
            ForEach-Object { [string]$_ }
    )

    $results = @()

    foreach ($member in $members) {
        $status = if ($member.Id -in $approvedIds) {
            "Approved"
        } else {
            "Unexpected Member"
        }

        $results += [PSCustomObject]@{
            TimestampUtc = [DateTime]::UtcNow.ToString("o")
            GroupName = $group.DisplayName
            GroupId = $group.Id
            UserId = $member.Id
            UserPrincipalName = $member.UserPrincipalName
            Status = $status
        }
    }

    foreach ($approvedId in $approvedIds) {
        if ($approvedId -notin @($members.Id)) {
            $results += [PSCustomObject]@{
                TimestampUtc = [DateTime]::UtcNow.ToString("o")
                GroupName = $group.DisplayName
                GroupId = $group.Id
                UserId = $approvedId
                UserPrincipalName = ""
                Status = "Missing Member"
            }
        }
    }

    return $results
}

try {
    # Validate configuration before querying Graph
    if (-not (Test-Path -LiteralPath $BaselinePath -PathType Leaf)) {
        throw "Baseline file not found: $BaselinePath"
    }

    $config = Get-Content -LiteralPath $BaselinePath -Raw |
        ConvertFrom-Json

    if (-not $config.tenantId -or
        @($config.groups).Count -eq 0) {
        throw "Baseline is missing tenantId or groups."
    }

    [void][guid]::Parse([string]$config.tenantId)

    $seenGroupIds = @()

    foreach ($definition in $config.groups) {
        [void][guid]::Parse([string]$definition.groupId)

        if ([string]::IsNullOrWhiteSpace($definition.displayName)) {
            throw "Baseline group is missing displayName."
        }

        if (@($definition.approvedUserIds).Count -eq 0) {
            throw "Group has no approved users: $($definition.displayName)"
        }

        if ($definition.groupId -in $seenGroupIds) {
            throw "Duplicate group ID in baseline."
        }

        foreach ($userId in $definition.approvedUserIds) {
            [void][guid]::Parse([string]$userId)
        }

        $seenGroupIds += $definition.groupId
    }

    Assert-GraphSession -ExpectedTenantId $config.tenantId

    # Collect all Graph results before writing reports
    $auditResults = @(
        foreach ($definition in $config.groups) {
            Write-Host "Auditing: $($definition.displayName)"

            Get-GroupAudit -Definition $definition
        }
    )

    $exceptions = @(
        $auditResults |
            Where-Object { $_.Status -ne "Approved" }
    )

    New-Item `
        -ItemType Directory `
        -Path $OutputDirectory `
        -Force | Out-Null

    $runId = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")

    $auditPath = Join-Path $OutputDirectory "audit-$runId.csv"
    $exceptionPath = Join-Path $OutputDirectory "exceptions-$runId.csv"

    $auditResults |
        Export-Csv -LiteralPath $auditPath `
        -NoTypeInformation -Encoding utf8

    if ($exceptions.Count -gt 0) {
        $exceptions |
            Export-Csv -LiteralPath $exceptionPath `
            -NoTypeInformation -Encoding utf8
    } else {
        # Create an empty report with column headers
        '"TimestampUtc","GroupName","GroupId","UserId","UserPrincipalName","Status"' |
            Set-Content -LiteralPath $exceptionPath -Encoding utf8
    }

    Write-Host ""
    Write-Host "Audit completed successfully."
    Write-Host "Findings: $($auditResults.Count)"
    Write-Host "Exceptions: $($exceptions.Count)"
    Write-Host "Audit report: $auditPath"
    Write-Host "Exception report: $exceptionPath"

    $auditResults |
        Format-Table GroupName, UserPrincipalName, Status -AutoSize
}
catch {
    Write-Warning "Audit failed or is incomplete: $($_.Exception.Message)"
    throw
}