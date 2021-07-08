

function check_service([string]$server_name, [string]$service_name){
    <#
    .SYNOPSIS
        True si le service existe sinon False
    .DESCRIPTION
        Check si un service est présent sur une machine distante.
    .PARAMETER server_name
        Nom du serveur pour lequel on check le service
    .PARAMETER service_name
        Nom du service
    .OUTPUTS
        True si existe sinon False
    #>
    Write-Host("Check du service : $service_name pour le serveur : $server_name")
    if(Get-Service -ComputerName "$server_name" -Name "$service_name" -erroraction 'Ignore')
    {
        return $true
    }
    else{
        return $false
    }
}


function checkZabbix($server_name){
    # Check si le service Zabbix agent est bien présent sur la machine
    Write-Host("Check Zabbix pour : $server_name")
    return check_service $server_name "Zabbix Agent"
}


function checkGraylog($server_name){
    <# Check si le service Graylog sidercar est installé
    Graylog sidercar permet d'etre détecté par graylog
    #>
    Write-Host("Check Graylog pour : $server_name")
    return check_service $server_name "graylog-sidercar"
}


function checkGraylogIsActive($server_name){
    <# Check si le service Graylog sidercar est bien configuré
        winlogbeat récupère les logs pour les envoyer sur graylog
    #>
    Write-Host("Check winlogbeat pour : $server_name")
    return check_service $server_name "graylog-collector-winlogbeat"
}


function test($server, [string]$service){
    $service
    Invoke-Command -ComputerName $server -ScriptBlock {
            Get-Service -Name "$service"
            if(Get-Service -Name "$service")
            {
                return $true
            }
            else{
                return $false
            }
        }
}

