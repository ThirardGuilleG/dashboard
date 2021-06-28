$server2019 = @("SRVT2SMTP","SRVT2WP", "SRVT2RDS", "SRVT2EB1",  "SRVT2EB2", "SRVY2WP", "SRVY2SQL", "SRVY2ARR", "SRVY2IISA", "SRVY2IISB", "SRVY2RPT", "SRVT2ETL",
                "VMCOMMUNICATION", "VMBOA", "SRVT2OXO", "SRVT2FS")


# (Get-HotFix -ComputerName "SRVT2WP" | Sort-Object -Property InstalledOn)[-1]

function fetchUpdates($pNameServer){
    Write-Host("Fetch des updates pour : $pNameServer")
    $r =Invoke-Command -ComputerName $pNameServer -ScriptBlock {
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateupdateSearcher()
        $Updates = @($UpdateSearcher.Search("IsHidden=0 and IsInstalled=0").Updates)
        $Updates 
        # Write-Host($Updates)
        # $Updates | Select-Object Title
        # $Updates
        # Write-Host([System.Environment]::OSVersion.Version)
        # $Updates | Select-Object Title | Export-Csv -Path ("c:\servers.csv") -Append -NoTypeInformation
    }
    return $r
}

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")

foreach($server in $server2019){
    $result = fetchUpdates($server)
    $body = $result | Select-Object Title,PSComputerName,MaxDownloadSize,IsDownloaded,IsInstalled,LastDeploymentChangeTime,RebootRequired,SupportUrl | ConvertTo-Json 
    $body
    # $result | Select-Object Title,PSComputerName,RebootRequired,MaxDownloadSize,Description | Export-Csv -Path (".\servers.csv") -Append -NoTypeInformation -Encoding UTF8 -Delimiter ";"
    # Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -Method POST -Body $body
    $response = Invoke-RestMethod 'http://127.0.0.1:5000/update/data' -Method 'POST' -Body $body -ContentType "application/json"
    $response | ConvertTo-Json
}
