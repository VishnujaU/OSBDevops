@echo off
REM Load properties from a file
setlocal enabledelayedexpansion

set PROPERTIES_FILE=D:\Azure\weblogic\deploy\DeployJar\config.properties

echo property files
REM Function to read property value from the properties file
for /F "tokens=1,* delims==" %%A in (%PROPERTIES_FILE%) do (
    set %%A=%%B
)
set CLASSPATH=C:\Oracle\Middleware\OracleHome\wlserver\server\lib\weblogic.jar;C:\Oracle\Middleware\OracleHome\wlserver\server\lib\wljmxclient.jar;C:\Oracle\Middleware\OracleHome\wlserver\server\lib\wlclient.jar;C:\Oracle\Middleware\OracleHome\wlserver\modules\features\wlst.wls.classpath.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.configfwk.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.kernel-api.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.alertfwk.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.services.core.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.kernel-wls.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.alertfwk.jar;C:\PROGRA~1\Java\JDK-18~1.0_4\lib\tools.jar;






set ORACLE_HOME=%oracle.home%
set MW_HOME=%middleware.home%
set WL_HOME=%wl.home%
set DOMAIN_HOME=%domain.home%
set OSB_HOME=%osb.home%
REM WebLogic Server details
set ADMIN_SERVER_URL=%admin.url%
set ADMIN_USER=%admin.user%
set ADMIN_PASS=%admin.password%
set TARGET_SERVER=%target.server%
set OSB_PROJECT_JAR=%osb.project.jar%
set OSB_CONFIG_FILE=%osb.config.file%
set WLST_SCRIPT_PATH=%wlst.script.path%

set CLASSPATH=C:\Oracle\Middleware\OracleHome\osb\lib\*;C:\Oracle\Middleware\OracleHome\osb\lib\modules\*;%CLASSPATH%
set CLASSPATH=C:\Oracle\Middleware\wlserver\server\lib\weblogic.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.kernel-wls.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.kernel-api.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.configfwk.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.config.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.runtime.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.management-api.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.management.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\com.bea.common.configfwk_1.8.0.0.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\com.bea.alsb.core.runtime_12.2.1.0.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.configfwk-wls.jar;C:\Oracle\Middleware\OracleHome\osb\lib\modules\oracle.servicebus.kernel-wls.jar;%CLASSPATH%

REM set WLST_SCRIPT_PATH=C:\Oracle\Middleware\OracleHome\oracle_common\common\bin\deploy1.py
set CUST_FILE_PATH=D:\Azure\weblogic\deploy\DeployJar\OSB_Customization.csv
set PROP_FILE_PATH=D:\Azure\weblogic\deploy\DeployJar\config.properties
REM Execute WLST script
call %WL_HOME%\common\bin\wlst.cmd %WLST_SCRIPT_PATH% %OSB_PROJECT_JAR% %CUST_FILE_PATH% %PROP_FILE_PATH%


echo %CLASSPATH%
REM Execute WLST script
echo call deploy.py
REM call C:\Oracle\Middleware\OracleHome\wlserver\common\bin\wlst.cmd %WLST_SCRIPT_PATH% %admin.url% %admin.user% %admin.password% %osb.project.jar% %osb.config.file% %session.name% 
echo OSB project deployed successfully.
pause
