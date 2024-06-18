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
# if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("Administrators")) { Start-Process powershell.exe "-File `"$PSCommandPath`"" -Verb RunAs; exit }

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
    $message = "Femtet マクロインターフェース設定に失敗しました。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
    throw $message
} else {
    write-host "regsvr32 OK"
}

# regsvr
regsvr32 $femtet_macro_dll_path  # returns nothing, dialog only

# win32com.client.makepy
py -m win32com.client.makepy FemtetMacro  # return nothing

# check constants setting
$ret = py -c "from win32com.client import constants, Dispatch;Dispatch('FemtetMacro.Femtet');print(constants.SOLVER_NONE_C)"
if (-not ($ret -eq "0")) {
    $title = "Error!"
    $message = "Femtet COM 定数設定に失敗しました。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
    throw $message
} else {
    write-host "makepy OK"
}

# make desktop shortcut for pyfemtet-opt-gui
$python_executable = py -c "import sys;print(sys.executable)"
$python_executable_dir = Split-Path $python_executable
$Scripts_dir = "NOT FOUND"  # null or empty string raises error in test-path
if ($python_executable_dir.EndsWith("Scripts")) {
    # i.e. for `venv` virtualenv
    $Scripts_dir = $python_executable_dir
} else  {
    # i.e. windows installer, miniforge, 
    $buff = Join-Path $python_executable_dir "Scripts"
    if (test-path $buff) {
        $Scripts_dir = $buff
    }
}
if (-not (Test-Path $Scripts_dir)) {
    $title = "warning"
    $message = "PyFmetet のインストールは完了しましたが、デスクトップにショートカットを作成できませんでした。"
    [System.Windows.Forms.MessageBox]::Show($message, $title)
} else {
    # create desktop shortcut of pyfemtet-opt.exe in $Scripts_dir folder
    $Target_exe = "$Scripts_dir\pyfemtet-opt.exe"
    $Shortcut_file = "$env:USERPROFILE\Desktop\pyfemtet-opt.lnk"
    
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($Shortcut_file)
    $Shortcut.TargetPath = $Target_exe
    $Shortcut.Save()
    
    # complete
    [System.Windows.Forms.MessageBox]::Show("PyFemtet インストール が完了しました。", "Complete!")

}

