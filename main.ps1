."$PSScriptRoot\check_services.ps1"
."$PSScriptRoot\checkUpdate.ps1"
."$PSScriptRoot\utils.ps1"


$server_url = "http://127.0.0.1:5000"
$token = '5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t'
enum Server_Version{
    WindowsServer19 = 19
    WindowsServer16 = 16
    WindowsServer12 = 12
    WindowsServer12R2 = 12.2
    WindowsServer08R2 = 08
}

$logger = [Logger]::new("MonitoBot")


function check_services(){
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        $etat = launch_check $Name
        $services = @{'server'=$Name; 'etat'=$etat}
        $url = "$server_url/admin/data"
        send_json -url $url -object_to_send $services
    }
}


function main(){
    $logger.info("Lancement du script d'obtention des updates et des états des services")
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        # Ajout de la rèfle pour récupérer les informations si besoin.
        addRuleForPSUpdate($Name)
        # Check les MAJ.
        $logger.info("Check des updates pour : $($Name)")
        $result = fetch_updates($Name)
        # Besoin de restart le serveur.
        $needRestart = Get-WURebootStatus -ComputerName $Name -Silent
        # Récupération Historique MAJ.
        $historyUpdate = getHistory($Name,1)
        # Objet à envoyer au serveur
        $toSend = @{'updates'=$result ;
        'history'=$historyUpdate;
        "needRestart"=$needRestart; 'server'= $Name}
        $toSend
        $url = "$server_url/update/data"
        send_json -url $url -object_to_send $toSend
        $logger.info("Check des services pour le serveur : $($Name)")
        $etat = launch_check $Name
        $dataToSend = @{'server'=$Name; 'etat'=$etat}
        $url = "$server_url/admin/data"
        send_json -url $url -object_to_send $dataToSend
        $logger.success("FIN des vérifications pour : $($Name)")
    }
    $logger.success("FIN du script")
}

main
# check_services
