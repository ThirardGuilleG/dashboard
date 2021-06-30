$server2019 = @("SRVT2SMTP","SRVT2WP", "SRVT2RDS", "SRVT2EB1",  "SRVT2EB2", "SRVY2WP", "SRVY2SQL", "SRVY2ARR", "SRVY2IISA", "SRVY2IISB", "SRVY2RPT", "SRVT2ETL",
                "VMCOMMUNICATION", "VMBOA", "SRVT2OXO", "SRVT2FS")


# (Get-HotFix -ComputerName "SRVT2WP" | Sort-Object -Property InstalledOn)[-1]

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
    # $response = Invoke-RestMethod 'http://127.0.0.1:5000/servers' -ContentType 'multipart/form-data'-Method 'POST' -Body $postParams
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/servers' -Method Post -Body $postParams;
    return $response | ConvertTo-Json
}

function main(){
    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "application/json")

    foreach($server in $server2019){
        $result = fetchUpdates($server)
        $body = $result | Select-Object Title,PSComputerName,MaxDownloadSize,IsDownloaded,IsInstalled,LastDeploymentChangeTime,RebootRequired,SupportUrl | ConvertTo-Json 
        # $result | Select-Object Title,PSComputerName,RebootRequired,MaxDownloadSize,Description | Export-Csv -Path (".\servers.csv") -Append -NoTypeInformation -Encoding UTF8 -Delimiter ";"
        # Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -Method POST -Body $body
        $response = Invoke-RestMethod 'http://127.0.0.1:5000/update/data' -Method 'POST' -Body $body -ContentType "application/json";
        $response | ConvertTo-Json;
    }
}


$servers = getServers | ConvertFrom-Json
foreach($server in $servers){
    $Name,$ip = $server.value
    Write-Host("Fetch update pour $($Name) ip : $($ip)")
    $result = fetchUpdates($Name)
    $body = $result | Select-Object Title,PSComputerName,MaxDownloadSize,IsDownloaded,IsInstalled,LastDeploymentChangeTime,RebootRequired,SupportUrl | ConvertTo-Json 
    $response = Invoke-RestMethod 'http://127.0.0.1:5000/update/data' -Method 'POST' -Body $body -ContentType "application/json";
    $response
}
