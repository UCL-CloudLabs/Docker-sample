# docker-sample
Docker sample to play with

This branch hosts the R calculator by David Col'quhoun and a script to serve it. Further instructions for properly opening ports etc can be found below.

## Instructions

- Run the instructions on [install.log] to install dependencies and make shiny-server run the app (this could be the script supplied to CloudLabs when deploying the VM).
- Change the network configuration so that the app is accessible on ports 3838 (used by existing users) *and* 80 (for simplicity, so that no port has to be supplied). This can be done in two ways:
  - \[a bit more involved but tested\] SSH into the VM and change the shiny server configuration file (`/etc/shiny-server/shiny-server.conf`) to `listen 80` instead of `3838`; then, through the Azure portal, add a new inbound rule (accessible through the entry for the Network Security Group) opening port 80 (Source: Any, Source port range: \*, Destination: Any, Destination port range: 80); similarly, add an incoming rule to redirect requests at port 3838 to 80 (Source: Any, Source port range: 3838, Destination: 80, Destination port range: 80).
  - \[should be simpler but not tested\] Set up an inbound rule redirecting port 80 to 3838.
 
 - It's possible that the following command is also required to be run from the VM, in addition to the Azure configuration:
 `sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 3838 -j REDIRECT --to-port 80`
