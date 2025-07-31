# CreditUnderwriting_Agentic_Workflow_Secured_App

Stop-Process -Name python

 Get-Process | Where-Object { $_.ProcessName -like "*python*" }

 netstat -ano | findstr :8000


 uvicorn CreditUnderwriting_Agentic_Workflow_Secured_App.main:app --reload