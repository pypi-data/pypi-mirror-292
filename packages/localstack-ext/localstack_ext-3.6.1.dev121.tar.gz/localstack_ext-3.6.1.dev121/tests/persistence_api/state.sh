#!/usr/bin/env bats

@test "test export state" {
	awslocal s3 mb s3://test-bucket
	run localstack state export
	tmp=$(echo $output | grep -o "success")
	[ -n "$tmp" ]
	[ $status -eq 0 ]
}

@test "test import state" {
	run localstack state import ls-state-export
	tmp=$(echo $output | grep -o "success")
	[ -n "$tmp" ]
	[ $status -eq 0 ]
}