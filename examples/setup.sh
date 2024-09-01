#!/bin/bash

su - ubuntu << 'EOF'

cd ~/

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# create venv
uv venv --python cpython-3.12.5-linux-x86_64-gnu
source .venv/bin/activate

# install superfetch
wget https://github.com/bfgbot/superfetch/releases/download/test/superfetch -O /tmp/superfetch
chmod +x /tmp/superfetch

uv pip install rq
tmux new-session -d -s ws_1 'rq worker superfetch --url redis://ip-172-31-31-165'

EOF
