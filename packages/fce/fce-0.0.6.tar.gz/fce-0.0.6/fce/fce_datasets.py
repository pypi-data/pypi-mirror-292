#!/usr/bin/env python3

def fce_datasets():
    import os
    cwd = os.getcwd()
    os.system("rm -rf "+cwd+"/homepage.iihe.ac.be")
    if os.path.isdir(cwd+"/datasets"):
        print("Please remove the datasets directory before downloading")
    else:
        os.system("wget -np -P . -r -R \"index.html*\" --cut-dirs=3 https://homepage.iihe.ac.be/~kskovpen/fce/datasets/; mv "+cwd+"/homepage.iihe.ac.be "+cwd+"/datasets")
