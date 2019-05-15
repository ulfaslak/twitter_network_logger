Worker scripts to run periodically for saving twitter interactions around a set of keywords.

1. [Create a gist on GitHub](https://gist.github.com/). It should only contain a dummy file (e.g. a short description of the dataset).
2. Enter the `data` folder and do `git init` and `git remote add origin <path_to_gist>.git.
3. Cache github credentials: `git config --global credential.helper "cache --timeout=<seconds>"`.
4. Do `git pull origin master` to get the dummy file from the gist. Type in your credentials.

5. Example execution `python worker.py --langs en,da --tags obama,trump`. 

