#!/usr/bin/env bash
# Retrieval QA battery: run ask.py on known questions and check the top hit.
cd "$(dirname "$0")" || exit 1
PY="env PYTHONPATH= ./.venv/bin/python"

check() {
  local q="$1" expect="$2"
  local out
  out=$($PY ask.py "$q" --topk 5 2>/dev/null)
  local top
  top=$(echo "$out" | grep -o -m1 '\[[A-Z]* čl\.[0-9]*[a-z]*[^]]*\]')
  if echo "$top" | grep -q "$expect"; then
    echo "PASS  [$top]  $q"
  else
    echo "FAIL  [$top] wanted [$expect]  $q"
  fi
}

check "what is the penalty for murder in Croatia"        "KZ čl.110"
check "penalty for aggravated murder"                     "KZ čl.111"
check "statute of limitations for criminal prosecution"  "KZ čl.81"
check "when can pre-trial detention be ordered"           "ZKP čl.123"
check "grounds for bail in criminal proceedings"          "ZKP čl.98"
check "who can file a criminal complaint"                 "ZKP čl.50"
check "penalty for fraud"                                 "KZ čl.236"
check "what is self-defense"                              "KZ čl.29"
check "penalty for theft"                                 "KZ čl.228"
check "rights of the suspect during interrogation"        "ZKP čl.39"
