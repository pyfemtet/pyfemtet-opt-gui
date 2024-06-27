# ===== DPI setting =====
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
[System.Windows.Forms.MessageBox]::Show("Femtet(2023.1以降) Python(3.11以降, 3.13未満) が必要です。インストールされていることを確認してから続けてください。", "pre-request")


# TODO: before run regsvr32, does it need to terminate femtet?


# ===== main =====

# install pyfemtet-opt-gui
py -m pip install pyfemtet-opt-gui -U --no-warn-script-location

# check pyfemtet-opt-gui installed
$installed_packages = py -m pip list
if (-not ($installed_packages | Select-String -Pattern 'pyfemtet-opt-gui')) {
    $title = "Error!"
    $message = "PyFemtet のインストールに失敗しました。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
    throw $message
}

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

# make desktop shortcut for pyfemtet-opt-gui
$pyfemtet_package_path = py -c "import pyfemtet;print(pyfemtet.__file__)"
$pyfemtet_opt_gui_path = $pyfemtet_package_path.replace("Lib\site-packages\pyfemtet\__init__.py", "Scripts\pyfemtet-opt.exe")
if (test-path $pyfemtet_opt_gui_path) {
    # create desktop shortcut of pyfemtet-opt.exe in $Scripts_dir folder
    $Shortcut_file = "$env:USERPROFILE\Desktop\pyfemtet-opt.lnk"    
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($Shortcut_file)
    $Shortcut.TargetPath = $pyfemtet_opt_gui_path
    $Shortcut.Save()
    write-host "create desktop shortcut: OK"
} else {
    $title = "warning"
    $message = "PyFmetet のインストールは完了しましたが、デスクトップにショートカットを作成できませんでした。Python 実行環境の Scripts フォルダ内の pyfemtet-opt.exe が見つかりません。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
}

[System.Windows.Forms.MessageBox]::Show("PyFemtet インストール が完了しました。", "Complete!")
