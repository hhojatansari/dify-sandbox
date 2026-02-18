jq -Rs --arg lang "python3" --argjson net false \
'{language:$lang, enable_network:$net, code:.}' \
./mock_fuse_scores_1.py \
| curl -sS -X POST "http://127.0.0.1:8194/v1/sandbox/run" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: dify-sandbox" \
  -d @-

jq -Rs --arg lang "python3" --argjson net false \
'{language:$lang, enable_network:$net, code:.}' \
./mock_fuse_scores_2.py \
| curl -sS -X POST "http://127.0.0.1:8194/v1/sandbox/run" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: dify-sandbox" \
  -d @-

jq -Rs --arg lang "python3" --argjson net false \
'{language:$lang, enable_network:$net, code:.}' \
./mock_merge_results.py \
| curl -sS -X POST "http://127.0.0.1:8194/v1/sandbox/run" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: dify-sandbox" \
  -d @-

