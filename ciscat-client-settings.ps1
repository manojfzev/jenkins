		    Set-ExecutionPolicy Unrestricted -Force
     		    Set-Service WinRM -StartMode Automatic
                Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
                $nfwRule = New-NetFirewallRule -DisplayName "Inboud Port 445" -Direction Inbound -LocalPort 445 -Protocol TCP -Action Allow
                Enable-NetFirewallRule -InputObject $nfwRule
                $nfwRule1 = New-NetFirewallRule -DisplayName "Inboud Port 5985" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow
                Enable-NetFirewallRule -InputObject $nfwRule1
                $regpath = "HKLM:SOFTWARE\Policies\Microsoft\Windows\WinRM\Service"
                New-ItemProperty -Path $regpath -Name "AllowAutoConfig" -Value "1" -PropertyType DWORD -Force
                New-ItemProperty -Path $regpath -Name "IPv4Filter" -Value "*" -PropertyType String -Force
                New-ItemProperty -Path $regpath -Name "IPv6Filter" -Value "*" -PropertyType String -Force
                New-ItemProperty -Path $regpath -Name "AllowUnencryptedTraffic" -Value "1" -PropertyType DWORD -Force
                Restart-Service WinRM
                $regpath1 = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
                New-ItemProperty -Path $regpath1 -Name "LocalAccountTokenFilterPolicy" -Value "1" -PropertyType DWORD -Force
                Enable-psremoting -force
                New-Item -Path $regpath -Name WinRS -Force
                $regpath2 = "HKLM:\Software\Policies\Microsoft\Windows\WinRM\Service\WinRS"
                New-ItemProperty -Path $regpath2 -Name "AllowRemoteShellAccess" -Value "1" -PropertyType DWORD -Force
                New-Item "C:\Temp" -Force -Type Directory
                net user /add localadmin "58=C*m@m5hRn7y(" /Y
		    net localgroup administrators localadmin /add
                gpupdate /force
                