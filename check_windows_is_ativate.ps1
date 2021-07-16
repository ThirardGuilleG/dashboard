# Get-CimInstance SoftwareLicensingProduct -Filter "Name like 'Windows%'" -ComputerName SRVT2OXO | where { $_.PartialProductKey } | select Description, LicenseStatus

# cscript c:\windows\system32\slmgr.vbs -dli