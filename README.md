ysnp
====
    sudo pip install virtualenvwrapper
    git clone git@github.com:Rdlgrmpf/ysnp.git

    # add this to bashrc
    source /usr/local/bin/virtualenvwrapper.sh
    export WORKON_HOME=~/.virtualenvs

    mkvirtualenv siam
    pip install -r requirements.txt

(C) Robin Morawetz, Janosch Frank, Franz Flintzer
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">YSNP</span> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
