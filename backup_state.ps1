# backup_state.ps1
Param(
  [string]$ContainerName = "routes_app-app-1",
  [string]$RepoRoot = (Get-Location).Path
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "$RepoRoot\backup_$timestamp"

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Копируем базу данных из контейнера
docker cp "$ContainerName:/app/data/routes.db" "$backupDir/routes.db"

# Архивируем состояние проекта (кроме backup)
$exclude = @("$backupDir","$RepoRoot\.git","$RepoRoot\backup*")
$items = Get-ChildItem -Path $RepoRoot -Recurse -Force | Where-Object {
  -not ($_.FullName -like "$backupDir*") -and -not ($_.FullName -like "$RepoRoot\.git*")
}
$paths = $items | ForEach-Object { $_.FullName }
Compress-Archive -Path $paths -DestinationPath "$backupDir/project.zip" -Force

Write-Host "Backup completed: $backupDir (project.zip, routes.db)"