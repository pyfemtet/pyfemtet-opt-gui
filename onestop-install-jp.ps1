﻿# ===== DPI setting =====
using assembly System.Windows.Forms
using namespace System.Windows.Forms
using namespace System.Drawing

Add-Type -Assembly System.Windows.Forms

#Enable visual styles
[Application]::EnableVisualStyles()

#Enable DPI awareness
$code = @"
    [System.Runtime.InteropServices.DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();
"@
$Win32Helpers = Add-Type -MemberDefinition $code -Name "Win32Helpers" -PassThru
$null = $Win32Helpers::SetProcessDPIAware()


# ===== pre-requirement =====

# --runas (reload)
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("Administrators")) { Start-Process powershell.exe "-File `"$PSCommandPath`"" -Verb RunAs; exit }

# error setting
$ErrorActionPreference = "Stop"

# message
$res = [System.Windows.Forms.MessageBox]::Show(
    "Femtet(2023.1以降), Python(3.11以降, 3.13未満) が必要です。インストールされていることを確認してから続けてください。",
    "pre-request",
    [System.Windows.Forms.MessageBoxButtons]::YesNo
)
if ($res -eq [System.Windows.Forms.DialogResult]::No) {
    throw '処理を取り消します。'
}


# TODO: before run regsvr32, does it need to terminate femtet?


# ===== main =====

write-host
write-host "======================"
write-host "installing pyfemtet..."
write-host "======================"
# install pyfemtet-opt-gui
py -m pip install pyfemtet-opt-gui -U --no-warn-script-location

# check pyfemtet-opt-gui installed
$installed_packages = py -m pip list
if (-not ($installed_packages | Select-String -Pattern 'pyfemtet-opt-gui')) {
    $title = "Error!"
    $message = "PyFemtet のインストールに失敗しました。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
    throw $message
} else {
    write-host "Install pyfemtet OK"
}


write-host
write-host "========================="
write-host "Enabling Python Macro ..."
write-host "========================="
# get Femtet.exe path using femtetuitls
$femtet_exe_path = py -c "from femtetutils import util;from logging import disable;disable();print(util.get_femtet_exe_path())"
# estimate FemtetMacro.dll path
$femtet_macro_dll_path = $femtet_exe_path.replace("Femtet.exe", "FemtetMacro.dll")
if (-not (test-path $femtet_macro_dll_path)) {
    $title = "Error!"
    $message = "Femtet マクロインターフェース設定に失敗しました。Femtet マクロヘルプを参照し「マクロの有効化」手順を実行してください。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
    throw $message
} else {
    write-host "regsvr32 will be OK"
}

# regsvr
regsvr32 $femtet_macro_dll_path  # returns nothing, dialog only


write-host
write-host "========================"
write-host "COM constants setting..."
write-host "========================"
# win32com.client.makepy
py -m win32com.client.makepy FemtetMacro  # return nothing

# check COM constants setting
$SOLVER_NON_C = py -c "from win32com.client import Dispatch, constants;Dispatch('FemtetMacro.Femtet');print(constants.SOLVER_NONE_C)"
if ($SOLVER_NON_C -eq "0") {
    write-host "COM constants setting: OK"
} else{
    $title = "warning"
    $message = "PyFmetet のインストールは完了しましたが、COM 定数設定に失敗しました。"
    $message += "コマンドプロンプトで下記のコマンドを実行してください。"
    $message += "\n py -m win32com.client.makepy FemtetMacro"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
}

write-host
write-host "==========================="
write-host "Create Desktop shortcuts..."
write-host "==========================="
# make desktop shortcut for pyfemtet-opt-gui
$pyfemtet_package_path = py -c "import pyfemtet;print(pyfemtet.__file__)"
$pyfemtet_opt_script_builder_path = $pyfemtet_package_path.replace("Lib\site-packages\pyfemtet\__init__.py", "Scripts\pyfemtet-opt.exe")
$pyfemtet_opt_result_viewer_path = $pyfemtet_package_path.replace("Lib\site-packages\pyfemtet\__init__.py", "Scripts\pyfemtet-opt-result-viewer.exe")

$succeed = $true
$succeed = (test-path $pyfemtet_opt_script_builder_path) -and (test-path $pyfemtet_opt_result_viewer_path)

if ($succeed) {
    # create desktop shortcut of pyfemtet-opt.exe in $Scripts_dir folder
    try {
        $Shortcut_file = "$env:USERPROFILE\Desktop\pyfemtet-opt.lnk"
        $WScriptShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WScriptShell.CreateShortcut($Shortcut_file)
        $Shortcut.TargetPath = $pyfemtet_opt_script_builder_path
        $Shortcut.Save()
    }
    catch {
        $succeed = $false
    }
    # plan to add 0.4.9
    # try {
    #     $Shortcut_file = "$env:USERPROFILE\Desktop\pyfemtet-opt-result-viewer.lnk"
    #     $WScriptShell = New-Object -ComObject WScript.Shell
    #     $Shortcut = $WScriptShell.CreateShortcut($Shortcut_file)
    #     $Shortcut.TargetPath = $pyfemtet_opt_result_viewer_path
    #     $Shortcut.Save()
    # }
    # catch {
    #     $succeed = $false
    # }
}

if ($succeed) {
    [System.Windows.Forms.MessageBox]::Show("PyFemtet インストールとセットアップが完了しました。", "Complete!")
} else {
    $title = "warning"
    $message = "PyFmetet のインストールは完了しましたが、デスクトップにショートカットを作成できませんでした。Python 実行環境の Scripts フォルダ内の pyfemtet-opt.exe が見つかりません。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)

}
