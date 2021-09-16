
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
    try {
        $updates = Get-WindowsUpdate -ComputerName $nameServer -ErrorAction Stop
        Write -host "fetch error $fetch_error"
        return $updates | Select-Object Size,Status,ComputerName,KB,Title,Description,Deadline,IsDownloaded,IsInstalled,MoreInfoUrls,RebootRequired,LastDeploymentChangeTime
    } catch {
        $logger.error("[$($name)] Problème dans l'obtention des MAJ : $($_)");
        Write-Host $_
    }
}

function getHistory($name, $NumberDayToFetch){
    try {
        $yesterday = Get-Date
        $yesterday = $yesterday.AddDays(-31).ToString("yyyy-MM-dd") 
        return Get-WUHistory -ComputerName $Name -MaxDate $yesterday -ErrorAction Stop | Select-Object ComputerName, OperationName, Date, Title, Result, KB 
    } catch {
        $logger.error("[$($name)] Problème dans l'obtention de l'historique des MAJ : $($_)");
        Write-Host $_
    }
}
