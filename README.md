# About
Worker script to run periodically for logging twitter interactions around a set of keywords.

# Usage
Link data is pushed to a Github gist, where it can be easily accessed from e.g. web-based data visualizations. Tweet and user data are stored locally. To get started:

1. Clone this repository.
2. [Create a gist on GitHub](https://gist.github.com/). It should only contain a dummy file (e.g. a short description of the dataset).
3. Enter the `data` folder and do `git init` and `git remote add origin <path_to_gist>.git`.
4. Cache github credentials: `git config --global credential.helper "cache --timeout=<seconds>"`.
5. Do `git pull origin master` to get the dummy file from the gist. Type in your credentials.
6. Enter a `screen` session on a server.
7. Execute the `worker.py` script with language and tag arguments. Example: `python worker.py --tags obama,trump --langs en,da`. 
