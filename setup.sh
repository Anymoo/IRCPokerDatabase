sudo apt-get update
sudo apt-get install sqlite3 libsqlite3-dev
sudo apt-get install sqlitebrowser

venv="./venv"

if ! [ -d "$venv" ]; then
  mkdir "$venv"
  virtualenv "$venv" --always-copy
  source "$venv/bin/activate"
  pip install -r ./requirement.txt
fi
