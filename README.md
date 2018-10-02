# golintpy
Simple python tool to analyse gometalinter results

Create a file with all the gometalinter reports
```SHELL
gometalinter --vendor --enable-all ./... > gometalinter_all
```

Then populate the issue-database (issue.db), after this you can query the data
```SHELL
python3 golint.py p < gometalinter_all
```

List all linters with issue-count
```SHELL
python3 golint.py l
```

List packages with issue-count
```SHELL
python3 golint.py pa
```

List files with issue-count
```SHELL
python3 golint.py f
```

List issues by lintername
```SHELL
python3 golint.py li lintername
```
