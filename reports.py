import pandas as pd
from server import *



def find_issues(rmc_servers, backedup_servers, source_path, filename=None):

    find_backedup_servers = {
        server.name.lower(): server
        for server in backedup_servers
    }

    rows = []

    for rmc_server in rmc_servers:

        backedUpServers = find_backedup_servers.get(
            rmc_server.name.lower()
        )

        # Server not found in RMC server list do nothing as it might be in another back up list
        if backedUpServers is None:
            continue

        rmc_server.foundinreports = source_path
        rmc_server.status = backedUpServers.status
        # Server found but backup not successful
        if backedUpServers.status != "Success":

            rows.append({
                "Server Name": rmc_server.name,
                "Backup Status": backedUpServers.status,
                "Found in report": rmc_server.foundinreports
            })

    if filename is not None:
        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False)
        print(f"Saved {len(df)} issues to {filename}")