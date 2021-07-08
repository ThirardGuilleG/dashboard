."$PSScriptRoot\check_services.ps1"
."$PSScriptRoot\checkUpdate.ps1"


function getServers(){
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "multipart/form-data")
    $postParams = @{token='5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t'}
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/servers' -Method Post -Body $postParams;
    return $response | ConvertTo-Json
}

function main(){
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        # Ajout de la rèfle pour récupérer les informations si besoin.
        addRuleForPSUpdate($Name)
        # Check les MAJ.
        Write-Host("Fetch update pour $($Name) ip : $($ip)")
        # $result = fetch_updates($Name)
        # Besoin de restart le serveur.
        # $needRestart = Get-WURebootStatus -ComputerName $Name -Silent
        # Récupération Historique MAJ.
        # $historyUpdate = getHistory($Name,1)
        # Etat des services
        $graylog = checkGraylog $Name
        $zabbix = checkZabbix $Name
        Write-Host "Etat graylog : $graylog"
        Write-Host "Etat zabbix : $zabbix"
        # Objet à envoyer au serveur
        $toSend = @{'updates'=$result ;
        'history'=$historyUpdate;
        "needRestart"=$needRestart; 'server'= $Name}
        # $toSend | ConvertTo-Json
        # $response = Invoke-RestMethod 'http://127.0.0.1:5000/update/data' -Method 'POST' -Body ($toSend | ConvertTo-Json) -ContentType "application/json";
        # $response
    }
}

main
