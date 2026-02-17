# In the project root:
```
python -m venv .venv
source .venv/bin/activate
pip install build
```

# 2) Build the package (creates wheel + sdist in ./dist/)
```
python -m build
```

# You should now have something like:
dist/pinballctl-0.1.0-py3-none-any.whl
dist/pinballctl-0.1.0.tar.gz


Create a new GITHUB release with

gh release create v0.1.0 dist/*

# To upgrade using a release

pip install --upgrade https://github.com/<you>/pinballctl/releases/download/v0.2.0/pinballctl-0.2.0-py3-none-any.whl
pinballctl service restart all