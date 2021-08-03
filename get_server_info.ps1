param ($server)
."$PSScriptRoot\utils.ps1"


$logger = [Logger]::new("MonitoBot")


function test_connectivity($server_name){
    if (Test-Connection $server_name -Count 1 -Quiet)
    {
        return $true
    }
    else{
        return $false
    }
}


function get_ip($server_name){ 
    $ping = Test-Connection $server_name -Count 1
    return $ping.IPV4Address.IPAddressToString
    }


function get_os([string]$server_dns_name){
    if ($server_dns_name -And (test_connectivity($server_dns_name))){
        $logger.info("Vérification de l'os pour $server_dns_name")
        $info = Invoke-Command -ComputerName $server_dns_name -ScriptBlock {Get-WmiObject Win32_OperatingSystem}
        $os = $info.name.split("|")[0]
        $logger.success("OS : $os")
        return $os    
    }
    return "Serveur non trouvé"
}

return get_ip $server
# return test_connectivity $server

