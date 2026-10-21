#import all required dependencies ----------------------------------
from dependencies import install_dependencies
install_dependencies()
from ui import select_sources, select_file
from server import (
    Server,
    RMCServer,
    VeeamServer,
    VeeamAZServer,
    CCLServer,
    BackupExecServer
)
from reports import (find_issues)
#--------------------------------------------------------------------

#trigger GUI in UI.py for report selection---------------------------
selected = select_sources()
# RMC always required
rmcReport = select_file("RMC patching required report")
onPremReport = None
azureReport = None
cclReport = None
backupexec_reports = []


rmc_servers = RMCServer.load_rmc_servers(rmcReport,sheet=0)
if selected["VeeamOnPrem"]: onPremReport = select_file("Veeam on Premises backup report")
if selected["VeeamAzure"]: azureReport = select_file("Veeam Azure backup report")
if selected["CCL"]:cclReport = select_file("CCL backup report")

for retention in [20, 30, 50, 60, 90]:

    if selected[f"BackupExec{retention}"]:

        backupexec_reports.append(
            select_file(
                f"BackupExec backup report {retention}",
                html=True
            )
        )
#---------------------------------------------------------------

#load server objects and find issues---------------------------
if onPremReport:

    veeam_on_prem_servers = (
        VeeamServer.load_veeam_servers(onPremReport, 6)
        + VeeamServer.load_veeam_servers(onPremReport, 2)
    )

    find_issues(
        rmc_servers,
        veeam_on_prem_servers,
        onPremReport
    )

if azureReport:

    veeam_azure_servers = (
        VeeamAZServer.load_azure_servers(
            azureReport
        )
    )
    find_issues(
            rmc_servers,
            veeam_azure_servers,
            azureReport
        )

if cclReport:

    ccl_servers = (
        CCLServer.load_ccl_servers(
            cclReport
        )
    )

    find_issues(
        rmc_servers,
        ccl_servers,
        cclReport
    )

#only used to collate backupexecservers for later
backupexec_servers = []

for report in backupexec_reports:
    servers = BackupExecServer.load_backup_exec_servers(report)

    if servers:
        find_issues(
            rmc_servers,
            servers,
            report
        )

    backupexec_servers.extend(servers)

RMCServer.save_staus_to_excel(
    rmc_servers,
    "rmc_servers_status.xlsx"
)