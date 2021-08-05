
function addRuleForPSUpdate($ServerName){
    # PSWindowsUpdate à besoin du port 143 en TCP et de la DLL dllhost(System32)
    $session = New-CimSession -ComputerName $ServerName
    # Get-NetFirewallRule -DisplayName <String[]>
    if (-Not (Get-NetFirewallRule -DisplayName "Allow PSWindowsUpdate TCP" -CimSession $session)){
        Write-Host "création route TCP pour : $($ServerName)"
        New-NetFirewallRule -DisplayName "Allow PSWindowsUpdate TCP" -Direction Inbound -LocalPort 143 -Protocol TCP -Action Allow -Profile Domain -CimSession $session;
    }
    if (-Not (Get-NetFirewallRule -DisplayName "Allow PSWindowsUpdate DLL" -CimSession $session)){
        Write-Host "création route DLL pour : $($ServerName)"
        New-NetFirewallRule -DisplayName "Allow PSWindowsUpdate DLL" -Direction Inbound -Program "%SystemRoot%\System32\dllhost.exe" -Action Allow -Profile Domain -CimSession $session;
    }
}

function fetch_updates($nameServer){
    $updates = Get-WindowsUpdate -ComputerName $nameServer
    return $updates | Select-Object Size,Status,ComputerName,KB,Title,Description,Deadline,IsDownloaded,IsInstalled,MoreInfoUrls,RebootRequired,LastDeploymentChangeTime
}

function getHistory($name, $NumberDayToFetch){
    $yesterday = Get-Date
    $yesterday = $yesterday.AddDays(-5).ToString("yyyy-MM-dd")
    return Get-WUHistory -ComputerName $Name -MaxDate $yesterday | Select-Object ComputerName, OperationName, Date, Title, Result, KB
}

