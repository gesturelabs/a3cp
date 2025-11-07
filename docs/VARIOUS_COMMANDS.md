#for FILE_TREE.txt
tree -a \
  -I '.git|.venv|env|a3cp-env|staticfiles|__pycache__|node_modules|dist|build|*.egg-info|*.pyc|*.pyo|*.pyd|*.log|*.sqlite3|*.db|.DS_Store|.mypy_cache|.ruff_cache|.pytest_cache|.idea|.vscode|.env|.env.*' \
  > docs/FILE_TREE.txt



#activate virtual env
source a3cp-env/bin/activate
