# Completion

Add the following commands to autocomplete ./bin/sp500

```
$ mkdir -p ~/.bash_completion.d
$ cp sp500_comp ~/.bash_completion.d
$ source ~/.bash_completion.d/*
$ complete -F _sp500 ../bin/sp500
```
