."$PSScriptRoot\utils.ps1"
# cscript c:\windows\system32\slmgr.vbs -dli

# logger
$logger = [Logger]::new("Windows_Activate_Bot")

function get_windows_state($computer_name){
    $state =  Get-CimInstance SoftwareLicensingProduct -Filter "Name like 'Windows%'" -ComputerName $computer_name | where { $_.PartialProductKey } | select Description, LicenseStatus;
    if($state.LicenseStatus -eq 1){
        return $true
        }
    else{
        return $false
        }
}

function main(){
    $logger.info("Lancement de la verification de l'activations des serveurs windows")
    foreach($server in (getServers | ConvertFrom-Json)){
        $name,$ip = $server.value
        $active_state = get_windows_state($name)
        if($active_state){
            $logger.success("Le serveur : $($name) est activé !")
        }
        else{
            $logger.warning("Le serveur : $($name) n'est pas activé !")
        }
        $logger.info("envoi de l'etat au serveur python")
        # url pour l'update en bdd
        $url = "http://127.0.0.1:5000/admin/active"
        $object = @{'server'=$name;'etat'=$active_state}
        send_json -url $url -object_to_send $object
    }
}

main