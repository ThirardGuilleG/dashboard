."$PSScriptRoot\utils.ps1"
# cscript c:\windows\system32\slmgr.vbs -dli

# logger
$logger = [Logger]::new("Windows_Activate_Bot")

function get_windows_state($computer_name){
    $state =  Get-CimInstance SoftwareLicensingProduct -Filter "Name like 'Windows%'" -ComputerName $computer_name | where { $_.PartialProductKey } | select Description, LicenseStatus;
    return [bool]$state.LicenseStatus
}

function main(){
    $logger.info("")
    foreach($server in (getServers | ConvertFrom-Json)){
        $Name,$ip = $server.value
        $active_state = get_windows_state($Name)
        if($active_state){
            $logger.success("Le serveur : $($Name) est activé !")
        }
        else{
            $logger.warning("Le serveur : $($Name) n'est pas activé !")
        }
    }
}