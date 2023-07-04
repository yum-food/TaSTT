#!/usr/bin/env bash

SERVER_IP="$1"
if [ -z "$SERVER_IP" ]; then
  echo "Usage: $0 server_ip"
  exit 1
fi
echo "Testing server at $SERVER_IP"

SESSION_ID_0=$(curl -s -X GET $SERVER_IP:8080/api/v0/create_session | awk -F':' '{print $2}' | tr -d '}')
echo "Got session id $SESSION_ID_0"
if [ -z "$SESSION_ID_0" ]; then
  echo "Expected session ID to be non-empty"
  exit 1
fi

echo "Initial transcript should be empty"
T0=$(curl -s -X GET -d "$SESSION_ID_0" $SERVER_IP:8080/api/v0/get_transcript)
if [ "$T0" != "" ]; then
  echo "Expected initial transcript to be empty, but got $T0"
  exit 1
fi
echo "Pass!"

echo "Should be able to update transcript once"
T1_EXP="foo bar"
curl -s -X POST -d "$SESSION_ID_0 $T1_EXP" $SERVER_IP:8080/api/v0/set_transcript

T1=$(curl -s -X GET -d "$SESSION_ID_0" $SERVER_IP:8080/api/v0/get_transcript)
if [ "$T1" != "$T1_EXP" ]; then
  echo "Expected transcript to be $T1_EXP, but got $T1"
  exit 1
fi
echo "Pass!"

echo "Subsequent update should overwrite"
T2_EXP="baz qux"
curl -s -X POST -d "$SESSION_ID_0 $T2_EXP" $SERVER_IP:8080/api/v0/set_transcript

T2=$(curl -s -X GET -d "$SESSION_ID_0" $SERVER_IP:8080/api/v0/get_transcript)
if [ "$T2" != "$T2_EXP" ]; then
  echo "Expected transcript to be $T2_EXP, but got $T2"
  exit 1
fi
echo "Pass!"

