#!/usr/bin/env bash
# Post-fix QA: full battery + targeted checks on previously-broken articles.
cd "$(dirname "$0")" || exit 1
export PYTHONPATH=
P=".venv/bin/python"

echo "========== test_qa.sh battery =========="
bash test_qa.sh 2>/dev/null

echo
echo "========== targeted checks (previously truncated articles) =========="
checks=(
  "what is the penalty for possessing drugs intended for sale|KZ čl.190"
  "maksimalno trajanje istražnog zatvora do presude|ZKP čl.133"
  "podaci o istovjetnosti osobe protiv koje je podnesena kaznena prijava službena tajna|ZKP čl.204"
  "kada sud odbija izvođenje dokaza na raspravi|ZKP čl.421"
  "zamjena novčane kazne radom za opće dobro|KZ čl.55"
  "uvjetna osuda opoziv|KZ čl.58"
  "presuda na temelju sporazuma stranaka|ZKP čl.360"
)
for c in "${checks[@]}"; do
  q="${c%%|*}"; want="${c##*|}"
  top=$($P ask.py "$q" --topk 4 2>/dev/null | grep -o -m1 '\[[A-Z]* čl\.[0-9]*[a-z]*\]')
  if echo "$top" | grep -q "$want"; then
    echo "PASS  [$top]  $q"
  else
    echo "FAIL  [$top] wanted [$want]  $q"
  fi
done

echo
echo "========== spot check: KZ 190 st.2 text retrievable =========="
$P ask.py "posjedovanje droge namijenjene prodaji kazna" --topk 2 2>/dev/null | head -8
