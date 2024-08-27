# INSTALL For PysswordSz
# Author: SidneyZhang<zly@lyzhang.me>

function PauseToExit {
    Write-Host "Press any key to continue..."
    [Console]::Readkey() | Out-Null
    Exit
}

$ErrorVersionText = @(
    "请使用PowerShell 5.0及以上版本，运行安装脚本..."
    "Please use PowerShell 5.0 or above to run the installation script..."
) -join "`n"

if ((Get-Host).Version.Major -le 5) {
    Write-Error $ErrorVersionText
    PauseToExit
}

$lang = @(
    "选择语言..."
    "Select your language..."
    "可以选择中文（zh)或英语（en)，"
    "You can select Chinese (zh) or English (en),"
    "请选择/Please Enter"
) -join "`n"

$lang = Read-Host $lang

$ErrorLangText = @(
    "仅支持中文（zh)或英语（en)，请重新运行脚本！"
    "Justly support Chinese (zh) or English (en), please run the script again!"
) -join "`n"

$file = Get-ChildItem pysswordsz*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($null -eq $file) {
    $text = @(
        "未找到压缩文件，请下载后再运行脚本！"
        "Not found the compressed file, please download and run the script again!"
    ) -join "`n"
    Write-Error $text
    PauseToExit
}

if ($lang -in "zh","en") {
    if ($lang -eq "zh") {
        $installPlace = Read-Host "输入需要的安装路径"

        if ((Test-Path $installPlace) -eq $false) {
            Write-Host "`n路径不存在，将创建对应路径..."
            New-Item -ItemType "directory" -Path $installPlace -
        }

        Write-Host "`n...开始安装PysswordSz..." -ForegroundColor DarkGreen
        Expand-Archive -Path $file.Name -DestinationPath $installPlace -Force
        Write-Host "`n复制完成，安装完成！" -ForegroundColor DarkGreen
    }
    else {
        $installPlace = Read-Host "Please enter the installation path"

        if ((Test-Path $installPlace) -eq $false) {
            Write-Host "`nPath is not exist, will create the corresponding path..."
            New-Item -ItemType "directory" -Path $installPlace
        }

        Write-Host "`n...Start installing PysswordSz..." -ForegroundColor DarkGreen
        Expand-Archive -Path $file.Name -DestinationPath $installPlace -Force
        Write-Host "`nCopy completed, installation completed!" -ForegroundColor DarkGreen
    }
    $envPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    [Environment]::SetEnvironmentVariable("PATH", "$envPath;$installPlace", "User")
    PauseToExit
}
else {
    Write-Error $ErrorLangText
    PauseToExit
}

