$server_url = "http://127.0.0.1:5000"
$token = '5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t'

$logger = [Logger]::new("MonitoBot")

function getServers(){
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "multipart/form-data")
    $postParams = @{token=$token}
    $response = Invoke-RestMethod -Uri "$server_url/servers" -Method Post -Body $postParams;
    return $response | ConvertTo-Json
}


function send_json{
    <#
    .SYNOPSIS
        Envoi d'une requete POST avec un objet JSON
    .PARAMETER url
        url pour le POST
    .PARAMETER object_to_send
        Objet powershell qui est converti en objet JSON
    .EXAMPLE
        $object = @{msg="An awsome test"}
        $url = "https://127.0.0.1/post"
        send_json($url, $object)
    #>
    param(
        [string]$url,
        [pscustomobject]$object_to_send
    )
    $response = Invoke-WebRequest -Uri $url -Method Post -Body ($object_to_send | ConvertTo-Json);
    # reponse
    if($response.StatusCode -lt 300){
        $logger.success("Envoi réussi")
    }else{
        $logger.error("Problème dans l'envoi à $url")
        Write-Host $response.StatusCode
    }
}


function install_PSWU{
    <#
    .SYNOPSIS
        Installation de PSWindowsUpdate si nécessaire
    #>
    $module = Get-Module -ListAvailable -Name PSWindowsUpdate
    if (-Not $module) {
        $logger.info("Moduel PSWindowsUpdate n'existe pas on l'install")
        Install-Module PSWindowsUpdate
    } 
}

enum graylog_log_type {
    <#
        Enum avec la correspondance des types de log
    #>
    info = 10
    success = 20
    warning = 30
    error = 40
    critical = 50
}

enum graylog_log_color {
    info = [System.ConsoleColor]::Cyan
    success = [System.ConsoleColor]::Green
    warning = [System.ConsoleColor]::Yellow
    error = [System.ConsoleColor]::Red
    critical = [System.ConsoleColor]::DarkRed
}

class Logger{
    <#
    .SYNOPSIS
        Class pour gérer l'envoi de log a un serveur graylog pour un input http gelf.
    .DESCRIPTION
        Envoi de log avec différent niveau(info,success,error...) en JSON
    .EXAMPLE
        $logger = [Logger]::new("MonitoBot")
    #>

    [string]$application_name
    [string]$hostname
    [string]$graylog_url

    Logger([string]$application_name){
        <#
        .SYNOPSIS 
            Constructeur
        .PARAMETER application_name
            Nom de l'application qui est utilisé pour différencier les logs sur graylog
        #>
        $this.application_name = $application_name
        $this.hostname = "$Env:COMPUTERNAME"
        $this.graylog_url = "https://graylog.thirard.fr:12222/gelf"
    }

    Logger([string]$application_name, [string]$hostname, [string]$graylog_url)
    {
        <#
        .SYNOPSIS 
            Constructeur
        .PARAMETER application_name
            Nom de l'application qui est utilisé pour différencier les logs sur graylog
        .PARAMETER hostname
            Host qui envoi les logs
        .PARAMETER graylog_url
            URL du de l'input graylog configuré en GELF HTTP
        #>
        $this.application_name = $application_name
        $this.hostname = $hostname
        $this.graylog_url = $graylog_url
    }

    [void] send_graylog ([string]$msg, [graylog_log_type]$log_type, [pscustomobject]$optional_json)
    {
        <#
        .SYNOPSIS
            Fonction d'envoi du log sur le serveur graylog
        .PARAMETER msg
            String
            message qui est envoyé à graylog
        .PARAMETER log_type
            enum graylog_log_type
            Type de log représenté par une valeur de l'enum graylog_log_type (info,success...)
        .PARAMETER optional_json
            Objet Powershell converti en json pour permettre l'envoi de plus d'information
        .EXAMPLE
            send_graylog("A sample message", [graylog_log_type]::success, $object_powershell)
        #>

        # Objet powershell qui sera envoyé à graylog
        $json = [pscustomobject]@{
            message = $msg
            host = $this.hostname
            log_type = $log_type.value__
            application = $this.application_name
            more_information = $optional_json
        }
        Write-Host "Debug : $([graylog_log_color]::$log_type)"
        $timestamp = Get-Date -Format o | ForEach-Object { $_ -replace ":", "." }
        Write-Host "$($timestamp)---$($log_type)---$($msg)" -ForeGroundColor ([graylog_log_color]::$log_type).value__
        $response = Invoke-WebRequest $this.graylog_url -Method 'POST' -Body ($json | ConvertTo-Json) -ContentType "application/json";
        if ($response.StatusCode -gt 300){
            Write-Host("Probléme dans l'envoi des logs") -ForeGroundColor Red
        }
    }

    [void] send_graylog ([string]$msg, [graylog_log_type]$log_type)
    {
        <#
        .SYNOPSIS
            Fonction d'envoi du log sur le serveur graylog
        .PARAMETER msg
            String
            message qui est envoyé à graylog
        .PARAMETER log_type
            enum graylog_log_type
            Type de log représenté par une valeur de l'enum graylog_log_type (info,success...)
        .EXAMPLE
            send_graylog("A sample message", [graylog_log_type]::success)
        #>

        # Objet powershell qui sera envoyé à graylog
        $json = [pscustomobject]@{
            message = $msg
            host = $this.hostname
            log_type = $log_type.value__
            application = $this.application_name
        }
        Write-Host "Debug : $([graylog_log_color]::$log_type)"
        $timestamp = Get-Date -Format o | ForEach-Object { $_ -replace ":", "." }
        Write-Host "$($timestamp)---$($log_type)---$($msg)" -ForeGroundColor ([graylog_log_color]::$log_type).value__
        $response = Invoke-WebRequest $this.graylog_url -Method 'POST' -Body ($json | ConvertTo-Json) -ContentType "application/json";
        if ($response.StatusCode -gt 300){
            Write-Host("Probléme dans l'envoi des logs") -ForeGroundColor Red
        }
    }

    [void] info([string]$msg, [pscustomobject]$optional_json){
        <#
        .SYNOPSIS
            Envoi d'un log d'information avec un objet json 
        .PARAMETER msg
            message qui est envoyé
        .PARAMETER optional_json
            Object Powershell qui est décomposée par Graylog pour permettre de rajouter des champs
        .EXAMPLE
            info("A sample info message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::info, $optional_json)
    }

    [void] info([string]$msg){
        <#
        .SYNOPSIS
            Envoi d'un log d'information avec un objet json 
        .PARAMETER msg
            message qui est envoy�
        .EXAMPLE
            info("A sample info message")
        #>
        $this.send_graylog($msg, [graylog_log_type]::info)
    }

    [void] success([string]$msg, [pscustomobject]$optional_json){
        <#
        .SYNOPSIS
            Envoi d'un log de succ�s avec objet json 
        .PARAMETER msg
            message qui est envoyé
        .PARAMETER optional_json
            Object Powershell qui est décomposée par Graylog pour permettre de rajouter des champs
        .EXAMPLE
            info("A sample success message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::success, $optional_json)
    }

    [void] success([string]$msg){
        <#
        .SYNOPSIS
            Envoi d'un log de succ�s
        .PARAMETER msg
            message qui est envoyé
        .EXAMPLE
            info("A sample success message")
        #>
        $this.send_graylog($msg, [graylog_log_type]::success)
    }

    [void] warning([string]$msg, [pscustomobject]$optional_json){
        <#
        .SYNOPSIS
            Envoi d'un log de warning avec un objet json 
        .PARAMETER msg
            message qui est envoyé
        .PARAMETER optional_json
            Object Powershell qui est décomposée par Graylog pour permettre de rajouter des champs
        .EXAMPLE
            info("A sample warning message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::warning, $optional_json)
    }

    [void] warning([string]$msg){
        <#
        .SYNOPSIS
            Envoi d'un log de warning
        .PARAMETER msg
            message qui est envoyé
        .EXAMPLE
            info("A sample warning message")
        #>
        $this.send_graylog($msg, [graylog_log_type]::warning)
    }

    [void] error([string]$msg, [pscustomobject]$optional_json){
        <#
        .SYNOPSIS
            Envoi d'un log d'erreur
        .PARAMETER msg
            message qui est envoyé
        .PARAMETER optional_json
            Object Powershell qui est décomposée par Graylog pour permettre de rajouter des champs
        .EXAMPLE
            info("A sample error message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::error, $optional_json)
    }

    [void] error([string]$msg){
        <#
        .SYNOPSIS
            Envoi d'un log d'erreur 
        .PARAMETER msg
            message qui est envoyé
        .EXAMPLE
            info("A sample error message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::error)
    }

    [void] critical([string]$msg, [pscustomobject]$optional_json){
        <#
        .SYNOPSIS
            Envoi d'un log critique avec objet json
        .PARAMETER msg
            message qui est envoyé
        .EXAMPLE
            info("A sample critical message", $powershell_object)
        #>
        $this.send_graylog($msg, [graylog_log_type]::critical, $optional_json)
    }

    [void] critical([string]$msg){
        <#
        .SYNOPSIS
            Envoi d'un log critique
        .PARAMETER msg
            message qui est envoyé
        .EXAMPLE
            info("A sample critical message")
        #>
        $this.send_graylog($msg, [graylog_log_type]::critical)
    }

}