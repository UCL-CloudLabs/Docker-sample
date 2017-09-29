git clone https://github.com/UCL-CloudLabs/docker-sample -b webmap repo
mv repo/index.html .
tmux new-session -d -s test 'python -m SimpleHTTPServer 8000'
