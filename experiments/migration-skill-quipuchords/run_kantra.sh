#!/usr/bin/env sh
# See a bug with https://github.com/konveyor/kantra/issues/676
export KANTRA_SKIP_MAVEN_CACHE=true
time kantra analyze --log-level 10 --input ./quipucords-ui --output ./kantra_output --target patternfly-v6 --enable-default-rulesets=false --provider=nodejs --rules rulesets/stable/nodejs/patternfly --overwrite
