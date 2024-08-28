#!/usr/bin/env bats

setup_file() {
  _pod_name_="bats-$(uuid)"
  export POD_NAME=$_pod_name_
  run localstack pod save $POD_NAME
}

@test "test save pod version" {
  awslocal s3 mb s3://test-bucket
  run localstack --debug pod save $POD_NAME
  # LocalStack 3.1.0. introduced a breaking change in the output of the save command (due to the introduction
  # of streaming endpoints, see #2513).
  if [[ "$LOCALSTACK_VERSION" == *"3.0"* ]]; then
    skip "pod save broken in $LOCALSTACK_VERSION"
  fi
  tmp=$(echo $output | grep -o "success")
  [ -n "$tmp" ]
  [ $status -eq 0 ]
}

@test "test pod versions" {
  run bash -c "localstack pod versions $POD_NAME --format json | jq '.[1].version'"
  [ "$output" = "2" ]
  [ $status -eq 0 ]
}

@test "delete delete not existing pod" {
  _not_ext_pod_="not-existing-pod-$(uuid)"
  run localstack pod delete $_not_ext_pod_
  tmp=$(echo $output | grep -o "not found")
  [ "$tmp" == "not found" ]
  [ -n "$tmp" ]
  [ $status -eq 1 ]
}

@test "test list pods" {
  localstack pod list
  [ $? -eq 0 ]
}

@test "test load pod" {
  localstack state reset
  buckets=$(echo $buckets | tr -d '\n\t')
  [ -z "$buckets" ]

  localstack pod load $POD_NAME -y
  [ $? -eq 0 ]
  buckets=$(awslocal s3 ls)
  [ -n "$buckets" ]
}

@test "test selective push" {
  # LocalStack 3.1.0. introduced a breaking change in the output of the save command (due to the introduction
  # of streaming endpoints, see #2513).
  if [[ "$LOCALSTACK_VERSION" == *"3.0"* ]]; then
    skip "pod save broken in $LOCALSTACK_VERSION"
  fi
  run awslocal sqs create-queue --queue-name test-queue
  run localstack pod save $POD_NAME --services sqs
  [ $status -eq 0 ]
  tmp=$(echo $output | grep -o "sqs")
  [ -n "$tmp" ]

  localstack state reset
  localstack pod load $POD_NAME
  [ $? -eq 0 ]
  buckets=$(awslocal s3 ls)
  [ -z "$buckets" ]

  queues=$(awslocal sqs list-queues)
  [ -n "$queues" ]
}

teardown_file() {
  run localstack pod delete $POD_NAME
}