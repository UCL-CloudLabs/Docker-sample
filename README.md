# docker-sample
Docker sample to play with

This branch hosts the R calculator by David Colqu'houn and a script to serve it. Further instructions for properly opening ports etc can be found below.

## Instructions
- Access the VM via ssh as `david@fpr-calculator.uksouth.cloudapp.azure.com`. Raquel, Anastasis and David C have the password.
- Run the instructions on [install.log](install.log) to install dependencies and make shiny-server run the app (this could be the script supplied to CloudLabs when deploying the VM).
- Change the network configuration so that the app is accessible on ports 3838 (used by existing users) *and* 80 (for simplicity, so that no port has to be supplied). This can be done in two ways:
  - \[a bit more involved\] SSH into the VM and change the shiny server configuration file (`/etc/shiny-server/shiny-server.conf`) to `listen 80` instead of `3838`; then, through the Azure portal, add a new inbound rule (accessible through the entry for the Network Security Group) opening port 80 (Source: Any, Source port range: \*, Destination: Any, Destination port range: 80); similarly, add an incoming rule to redirect requests at port 3838 to 80 (Source: Any, Source port range: 3838, Destination: 80, Destination port range: 80). Note: a rule opening port 3838 will also be required unless this was done during the VM deployment.
  - \[a bit simpler\] Set up an inbound rule redirecting port 80 to 3838, and additional rules opening ports 80 and 3838. This only saves editing the server configuration file.
 
 - It's possible that the following command is also required to be run from the VM, in addition to the Azure configuration:

`sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 3838 -j REDIRECT --to-port 80`
 
 (or swapping 80 and 3838 if following the second way above)

- If the ports are not open, despite the rules on the Azure portal:

`sudo iptables -A INPUT -i eth0 -p tcp --dport 80 -j ACCEPT`

`sudo iptables -A INPUT -i eth0 -p tcp --dport 3838 -j ACCEPT`

- The network rules will normally be lost if the machine reboots. They can be saved to a file using `iptables-save` and automatically reloaded at reboot [using the `iptables-persistent` package](https://www.thomas-krenn.com/en/wiki/Saving_Iptables_Firewall_Rules_Permanently#iptables-persistent_for_Debian.2FUbuntu). The file can also be monitored for unexpected changes using the `auditctl` and `ausearch` commands.

- After changing the configuration file, shiny-server has to be restarted with:
`sudo systemctl restart shiny-server`
