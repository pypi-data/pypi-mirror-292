#!/bin/bash

version=0.1.0

mvn clean

mvn package -Pscala11
cp target/localstack-emr-test-$version-shaded.jar target/localstack-emr-test-$version-scala11-shaded.jar

mvn package -Pscala12
cp target/localstack-emr-test-$version-shaded.jar target/localstack-emr-test-$version-scala12-shaded.jar
