
function addRuleForPSUpdate($ServerName){
    # PSWindowsUpdate à besoin du port 143 en TCP et de la DLL dllhost(System32)

    Write-Host "création route pour : $($ServerName)"
    $session = New-CimSession -ComputerName $ServerName
    New-NetFirewallRule -DisplayName "Allow PSWindowsUpdate TCP" -Direction Inbound -LocalPort 143 -Protocol TCP -Action Allow -CimSession $session
    New-NetFirewallRule -DisplayName "Allow PSWindowsUpdate DLL" -Direction Inbound -Program "%SystemRoot%\System32\dllhost.exe" -Action Allow -CimSession $session
}

function betterFetchUpdates($nameServer){
    $updates = Get-WindowsUpdate -ComputerName $nameServer 
    return $updates | Select-Object Size,Status,ComputerName,KB,Title,Description,Deadline,IsDownloaded,IsInstalled,MoreInfoUrls,RebootRequired
}


function fetchUpdates($pNameServer){
    $r =Invoke-Command -ComputerName $pNameServer -ScriptBlock {
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateupdateSearcher()
        $Updates = @($UpdateSearcher.Search("IsHidden=0 and IsInstalled=0").Updates)
        $Updates 
    }
    return $r
}

function getServers(){
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "multipart/form-data")
    $postParams = @{token='5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t'}
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/servers' -Method Post -Body $postParams;
    return $response | ConvertTo-Json
}

function main(){
    $yesterday = Get-Date
    $yesterday.AddDays(-1).ToString("yyyy-MM-dd")
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        Write-Host("Fetch update pour $($Name) ip : $($ip)")
        $result = betterFetchUpdates($Name)
        $needRestart = Get-WURebootStatus -ComputerName $Name -Silent
        $historyUpdate = Get-WUHistory -ComputerName $Name -MaxDate $yesterday
        $toSend = @{'updates'=$result ;
        'history'=$historyUpdate;
        "needRestart"=$needRestart}
        $toSend | ConvertTo-Json
        $response = Invoke-RestMethod 'http://127.0.0.1:5000/update/data' -Method 'POST' -Body ($toSend | ConvertTo-Json) -ContentType "application/json";
        $response
    }
    
}



# fetchUpdates("SRVT2OXO")

main