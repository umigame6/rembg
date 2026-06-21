$u=[Environment]::GetEnvironmentVariable('PATH','User')
$a='C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\x64'
if(-not $u) {
    [Environment]::SetEnvironmentVariable('PATH',$a,'User')
    Write-Host 'ADDED_TO_USER_PATH'
} elseif ($u -notlike '*v13.1*bin*x64*') {
    [Environment]::SetEnvironmentVariable('PATH', $u + ';' + $a, 'User')
    Write-Host 'ADDED_TO_USER_PATH'
} else {
    Write-Host 'ALREADY_IN_USER_PATH'
}

if (([Environment]::GetEnvironmentVariable('PATH','User')) -match 'v13.1\\bin\\x64') {
    Write-Host 'VERIFY_OK'
} else {
    Write-Host 'VERIFY_FAILED'
}