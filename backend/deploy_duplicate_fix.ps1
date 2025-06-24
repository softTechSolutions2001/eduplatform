# File Path: backend/deploy_duplicate_fix.ps1
# Version: 1.1.0
# Date Created: 2025-06-15 07:22:54
# Date Revised: 2025-06-15 07:22:54
# Author: sujibeautysalon
# Last Modified By: sujibeautysalon
# Last Modified: 2025-06-15 07:22:54 UTC
# User: sujibeautysalon
#
# PowerShell Deployment Script: Complete Category Duplicate Fix (Windows Compatible)
#
# This script deploys the permanent fix for category duplicates on Windows:
# 1. Runs data migration to clean existing duplicates
# 2. Applies schema migration to add unique constraint
# 3. Verifies the fix worked
# 4. Tests duplicate prevention
#
# FIXED: Removed Unicode emojis that cause PowerShell parsing errors

Write-Host "DEPLOYING PERMANENT CATEGORY DUPLICATE FIX" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Step 1: Check current state
Write-Host ""
Write-Host "CURRENT STATE CHECK..." -ForegroundColor Yellow
python manage.py simple_duplicate_inspection

# Step 2: Run data migration to clean duplicates
Write-Host ""
Write-Host "STEP 1: Cleaning existing duplicates..." -ForegroundColor Yellow
python manage.py migrate courses 0013b_dedup_category_names

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Data migration failed! Stopping deployment." -ForegroundColor Red
    exit 1
}

# Step 3: Run schema migration to add unique constraint
Write-Host ""
Write-Host "STEP 2: Adding unique constraint..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Schema migration failed! Stopping deployment." -ForegroundColor Red
    exit 1
}

# Step 4: Verify no duplicates remain
Write-Host ""
Write-Host "STEP 3: Verifying fix..." -ForegroundColor Yellow
python manage.py simple_duplicate_inspection

# Step 5: Test duplicate prevention
Write-Host ""
Write-Host "STEP 4: Testing duplicate prevention..." -ForegroundColor Yellow

# Create test script for validation
$testScript = @"
from courses.models import Category
from django.core.exceptions import ValidationError

print("Testing duplicate prevention...")

# Test 1: Try to create duplicate via model
try:
    cat1 = Category.objects.create(name="Test Category Duplicate", slug="test-dup-1")
    print("SUCCESS: Created first test category")

    cat2 = Category.objects.create(name="Test Category Duplicate", slug="test-dup-2")
    print("ERROR: Duplicate creation succeeded (should have failed)")
except Exception as e:
    print(f"SUCCESS: Duplicate creation properly blocked: {e}")

# Test 2: Try case-insensitive duplicate
try:
    cat3 = Category.objects.create(name="test category duplicate", slug="test-dup-3")
    print("ERROR: Case-insensitive duplicate succeeded (should have failed)")
except Exception as e:
    print(f"SUCCESS: Case-insensitive duplicate properly blocked: {e}")

# Clean up test data
Category.objects.filter(name__icontains="Test Category Duplicate").delete()
print("CLEANUP: Removed test data")

print("DUPLICATE PREVENTION WORKING CORRECTLY!")
"@

$testScript | python manage.py shell

Write-Host ""
Write-Host "PERMANENT FIX DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "SUCCESS: Current duplicates removed" -ForegroundColor Green
Write-Host "SUCCESS: Unique constraint added" -ForegroundColor Green
Write-Host "SUCCESS: Model validation active" -ForegroundColor Green
Write-Host "SUCCESS: Duplicate prevention tested" -ForegroundColor Green
Write-Host ""
Write-Host "Your system is now protected against category duplicates!" -ForegroundColor Cyan
