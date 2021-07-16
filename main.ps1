."$PSScriptRoot\check_services.ps1"
."$PSScriptRoot\checkUpdate.ps1"
$server_url = "http://127.0.0.1:5000"
$token = '5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t'
enum Server_Version{
    WindowsServer19 = 19
    WindowsServer16 = 16
    WindowsServer12 = 12
    WindowsServer12R2 = 12.2
    WindowsServer08R2 = 08
}


function getServers(){
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "multipart/form-data")
    $postParams = @{token=$token}
    $response = Invoke-RestMethod -Uri "$server_url/servers" -Method Post -Body $postParams;
    return $response | ConvertTo-Json
}


function check_services(){
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        $etat = launch_check $Name
        $services = @{'server'=$Name; 'etat'=$etat}
        $response = Invoke-RestMethod "$server_url/admin/data" -Method 'POST' -Body ($services | ConvertTo-Json) -ContentType "application/json";
        Write-Host $response -ForeGroundColor Green
    }
}


function main(){
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        # Ajout de la rèfle pour récupérer les informations si besoin.
        addRuleForPSUpdate($Name)
        # Check les MAJ.
        Write-Host("Fetch update pour $($Name) ip : $($ip)")
        $result = fetch_updates($Name)
        # Besoin de restart le serveur.
        $needRestart = Get-WURebootStatus -ComputerName $Name -Silent
        # Récupération Historique MAJ.
        $historyUpdate = getHistory($Name,1)
        # Objet à envoyer au serveur
        $toSend = @{'updates'=$result ;
        'history'=$historyUpdate;
        "needRestart"=$needRestart; 'server'= $Name}
        $response = Invoke-RestMethod "$server_url/update/data" -Method 'POST' -Body ($toSend | ConvertTo-Json) -ContentType "application/json";
        Write-Host $response -ForeGroundColor Green
        # Etat des services
        $etat = launch_check $Name
        $dataToSend = @{'server'=$Name; 'etat'=$etat}
        $response = Invoke-RestMethod "$server_url/admin/data" -Method 'POST' -Body ($dataToSend | ConvertTo-Json) -ContentType "application/json";
        Write-Host $response -ForeGroundColor Green
    }
}

main
# check_services
