# Register Windows Scheduled Task for Weekday 8:00 PM NAV Fetch & ETL
$Action = New-ScheduledTaskAction -Execute "C:\Users\Administrator\AppData\Local\Programs\Python\Python38\python.exe" -Argument "run_pipeline.py" -WorkingDirectory "F:\Bluestock Capstone"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 8:00PM
Register-ScheduledTask -TaskName "Bluestock_MF_Weekday_ETL" -Action $Action -Trigger $Trigger -Force
Write-Host "Registered Bluestock_MF_Weekday_ETL for Mon-Fri at 8:00 PM"
