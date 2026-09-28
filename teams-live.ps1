param([switch]$Once)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class TeamsCapture {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
'@
[TeamsCapture]::SetProcessDPIAware() | Out-Null
$textCondition=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Text)
$lastImage=[datetime]::MinValue
$window=$null
$captionGroup=$null
while($true){
 try{
  if($null -eq $window){
   $ids=@(Get-Process ms-teams,Teams -ErrorAction SilentlyContinue | ForEach-Object Id)
   $windows=[System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition)
   foreach($candidate in $windows){
    if($ids -contains $candidate.Current.ProcessId -and $candidate.Current.Name -match 'Besprechung|Meeting|Meeting now|Собрание'){$window=$candidate;break}
   }
  }
  if($null -eq $window){throw 'Окно встречи Teams не найдено'}
  $current=$window.Current
  if($captionGroup){try{$null=$captionGroup.Current.ProcessId}catch{$captionGroup=$null}}
  if($null -eq $captionGroup){
   $groups=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::Group)))
   foreach($group in $groups){if($group.Current.Name -match '^(Liveuntertitel|Live captions|Captions|Субтитры)$'){$captionGroup=$group;break}}
  }
  $captions=@();$speaker=''
  if($captionGroup){
   foreach($item in $captionGroup.FindAll([System.Windows.Automation.TreeScope]::Descendants,$textCondition)){
    $text=($item.Current.Name -replace '\s+',' ').Trim()
    if($text -match '\([^,()]+,\s*[^()]+\)'){$speaker=$text;continue}
    if($speaker -and $text -and $text -notmatch '^(RTT|Liveuntertitel|Live captions)' -and $text -notmatch 'Microsoft-Datenschutz'){
     $captions+=@{id=($item.GetRuntimeId()-join '.');speaker=$speaker;text=$text}
    }
   }
  }
  $result=@{time=[DateTimeOffset]::Now.ToUnixTimeMilliseconds();window=$current.Name;captions=$captions;captionsAvailable=($null -ne $captionGroup)}
  if(((Get-Date)-$lastImage).TotalSeconds -ge 30){
   $lastImage=Get-Date
   $captionIds=@{}
   if($captionGroup){foreach($element in $captionGroup.FindAll([System.Windows.Automation.TreeScope]::Descendants,$textCondition)){$captionIds[($element.GetRuntimeId()-join '.')]=1}}
   $uiText=@()
   foreach($element in $window.FindAll([System.Windows.Automation.TreeScope]::Descendants,$textCondition)){
    if($element.Current.IsOffscreen -or $captionIds.ContainsKey(($element.GetRuntimeId()-join '.'))){continue}
    $name=$element.Current.Name
    if($name -and $name -notmatch '\([^,()]+,\s*[^()]+\)' -and $name -notmatch '^\d+[/:]\d+'){$uiText+=$name}
   }
   $result.screenText=($uiText -join "`n")
   $handle=[IntPtr]$current.NativeWindowHandle
   $rect=$current.BoundingRectangle
   $shared=$null
   $menuItems=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,(New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty,[System.Windows.Automation.ControlType]::MenuItem)))
   foreach($item in $menuItems){if($item.Current.Name -match 'freigegebener Inhalt|shared content' -and -not $item.Current.IsOffscreen){$shared=$item;break}}
   if($null -eq $shared){$result.screenError='Презентация сейчас не показывается: область демонстрации не найдена'}
   elseif(-not [TeamsCapture]::IsIconic($handle) -and $rect.Width -gt 100 -and $rect.Height -gt 100){
    $bitmap=New-Object System.Drawing.Bitmap([int]$rect.Width,[int]$rect.Height)
    $graphics=[System.Drawing.Graphics]::FromImage($bitmap)
    try{
     $dc=$graphics.GetHdc()
     try{$ok=[TeamsCapture]::PrintWindow($handle,$dc,2)}finally{$graphics.ReleaseHdc($dc)}
     if($ok){
      $bounds=$shared.Current.BoundingRectangle
      $crop=[System.Drawing.Rectangle]::new([int]($bounds.X-$rect.X),[int]($bounds.Y-$rect.Y),[int]$bounds.Width,[int]$bounds.Height)
      if($crop.X -lt 0 -or $crop.Y -lt 0 -or $crop.Width -lt 100 -or $crop.Height -lt 100 -or $crop.Right -gt $bitmap.Width -or $crop.Bottom -gt $bitmap.Height){throw 'Границы презентации недоступны'}
      $presentation=$bitmap.Clone($crop,$bitmap.PixelFormat)
      $memory=New-Object System.IO.MemoryStream
      try{$presentation.Save($memory,[System.Drawing.Imaging.ImageFormat]::Jpeg);$result.imageBase64=[Convert]::ToBase64String($memory.ToArray());$result.imageTime=[DateTimeOffset]::Now.ToUnixTimeMilliseconds();$result.screenText='';$result.scope='teams-presentation'}finally{$memory.Dispose();$presentation.Dispose()}
     }else{$result.screenError='Teams не отдал изображение окна'}
    }finally{$graphics.Dispose();$bitmap.Dispose()}
   }else{$result.screenError='Окно Teams свёрнуто: свежий скрин недоступен'}
  }
  $result | ConvertTo-Json -Depth 5 -Compress
 }catch{
  @{time=[DateTimeOffset]::Now.ToUnixTimeMilliseconds();error=$_.Exception.Message} | ConvertTo-Json -Compress
  $window=$null
  $captionGroup=$null
 }
 if($Once){break}
 Start-Sleep -Milliseconds 1000
}
