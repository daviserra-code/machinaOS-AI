# Deploy static Vite site to Hetzner without requiring git push first.
# Optional: use -PushToGit to commit and push after successful deployment.
#
# Examples:
#   .\deploy-to-hetzner.ps1
#   .\deploy-to-hetzner.ps1 -PushToGit -CommitMessage "Update site"

param(
    [string]$CommitMessage = "Update deployment",
    [switch]$PushToGit,
    [string]$ServerIp = "46.224.91.14",
    [string]$ServerUser = "root",
    [string]$ProjectPath = "/opt/machina",
    [string]$WebRoot = "/var/www/machina-intelligence"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting deployment to Hetzner..." -ForegroundColor Cyan

# Step 1: Build locally so deployment can happen before any git push.
Write-Host "`nBuilding production assets locally..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Deployment aborted." -ForegroundColor Red
    exit 1
}

# Step 2: Ensure remote directories exist.
Write-Host "Ensuring remote directories exist..." -ForegroundColor Yellow
ssh "${ServerUser}@${ServerIp}" "mkdir -p $ProjectPath $WebRoot"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create remote directories." -ForegroundColor Red
    exit 1
}

# Step 3: Clean and upload dist/.
Write-Host "Uploading dist/ to server..." -ForegroundColor Yellow
ssh "${ServerUser}@${ServerIp}" "find $WebRoot -mindepth 1 -delete || true"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to clean remote web root." -ForegroundColor Red
    exit 1
}

scp -r dist/* "${ServerUser}@${ServerIp}:${WebRoot}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upload build artifacts." -ForegroundColor Red
    exit 1
}

# Step 4: Fix permissions so Nginx (www-data) can read all uploaded files.
Write-Host "Fixing file permissions..." -ForegroundColor Yellow
ssh "${ServerUser}@${ServerIp}" "chown -R www-data:www-data $WebRoot && find $WebRoot -type d -exec chmod 755 {} + && find $WebRoot -type f -exec chmod 644 {} +"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: permission fix failed - CSS/JS may not load." -ForegroundColor Yellow
}

Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
Write-Host "Live at: https://machina-intelligence.com" -ForegroundColor Cyan

# Optional step: commit and push after successful deploy.
if ($PushToGit) {
    Write-Host "`nCommitting and pushing to GitHub..." -ForegroundColor Yellow
    git add -A
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Nothing to commit." -ForegroundColor Yellow
        exit 0
    }
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git push failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Git push completed." -ForegroundColor Green
}
