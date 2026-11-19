#import all required dependencies not in default Python library using install_dependencies() ----------------------------------
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
#--------------------------------------------------------------------------------------------------------------------------------

#trigger GUI in UI.py for report selection---------------------------------------------------------------------------------------
selected = select_sources()
rmcReport = None
onPremReportPDF = None
azureReportPDF = None
onPremVMReportCSV = None
onPremAGTReportCSV = None
azureReportCSV = None
cclReport = None
backupexec_reports = []


#prompt user to select file based on values returned from select sources however RMC Report is always required------------------
if any(selected.values()):rmcReport = select_file("RMC patching required report")
if selected["VeeamOnPrem(PDF)"]: onPremReportPDF = select_file("Veeam on Premises backup report PDF","PDF")
if selected["VeeamAzure(PDF)"]: azureReportPDF = select_file("Veeam Azure backup report PDF","PDF")
if selected["VeeamOnPrem(CSV)"]: 
    onPremVMReportCSV = select_file("Veeam on Premises VM backup report CSV","CSV")
    onPremAGTReportCSV = select_file("Veeam on Premises AGT backup report CSV","CSV")
if selected["VeeamAzure(CSV)"]: azureReportCSV = select_file("Veeam Azure backup report CSV","CSV")
if selected["CCL"]:cclReport = select_file("CCL backup report","CSV")

for retention in [20, 30, 50, 60, 90]:
    if selected[f"BackupExec{retention}"]:
        backupexec_reports.append(
            select_file(
                f"BackupExec backup report {retention}",
                html=True
            )
        )

#----------------------------------------------------------------------------------------------------------------------------------

#load server objects and find issues. This only triggers if a checkbox has been hit. ----------------------------------------------
if any(selected.values()):
    if rmcReport:
        rmc_servers = RMCServer.load_rmc_servers(rmcReport,sheet=0)

    if onPremReportPDF:
        
        veeam_on_prem_servers = (
            VeeamServer.load_veeam_servers_PDF(onPremReportPDF)
        )
        find_issues(
            rmc_servers,
            veeam_on_prem_servers,
            onPremReportPDF
        )
        Server.save_status_to_excel(veeam_on_prem_servers,"veeam_onprem_servers_PDF_loaded.xlsx")
    
    if azureReportPDF:

        veeam_azure_servers = (
            VeeamAZServer.load_azure_servers_PDF(
                azureReportPDF
            )
        )
        find_issues(
                rmc_servers,
                veeam_azure_servers,
                azureReportPDF
            )
        Server.save_status_to_excel(veeam_azure_servers,"veeam_Azure_servers_PDF_loaded.xlsx")

    if onPremVMReportCSV or onPremAGTReportCSV:

        veeam_on_prem_servers = (
            VeeamServer.load_veeam_servers_CSV(onPremVMReportCSV)
            + VeeamServer.load_veeam_servers_CSV(onPremAGTReportCSV,"AGT")
        )
        find_issues(
            rmc_servers,
            veeam_on_prem_servers,
            onPremVMReportCSV
        )
        Server.save_status_to_excel(veeam_on_prem_servers,"veeam_onprem_servers_CSV_loaded.xlsx")

    if azureReportCSV:

        veeam_azure_servers = (
            VeeamAZServer.load_azure_servers_CSV(
                azureReportCSV
            )
        )
        find_issues(
                rmc_servers,
                veeam_azure_servers,
                azureReportCSV
            )
        Server.save_status_to_excel(veeam_azure_servers,"veeam_azure_servers_CSV_loaded.xlsx")

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

    Server.save_status_to_excel(
        rmc_servers,
        "rmc_servers_status.xlsx",
        "RMCCheck"
    )