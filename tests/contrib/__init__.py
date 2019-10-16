# Do *NOT* `import oteltrace` in here
# DEV: Some tests rely on import order of modules
#   in order to properly function. Importing `oteltrace`
#   here would mess with those tests since everyone
#   will load this file by default
