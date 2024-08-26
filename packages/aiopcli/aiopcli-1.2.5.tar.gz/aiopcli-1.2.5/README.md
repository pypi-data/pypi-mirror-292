# aiopcli

## Installation

```
pip install aiopcli
```

## Examples

```
# 単体コンテナイメージを登録
# デフォルトapi serverポートが8080

$ aiopcli image push my-image

{"imageId": "i-0123456789"}

$ aiopcli servable create --name=my-servable \
    --api-server=i-0123456789 \
    --api-port=80 \
    --liveness-endpoint=/health \
    --readiness-endpoint=/health

{"servableId": "s-z15uerp3mehdxg33"}

$ aiopcli env create --tag=test --servable=s-z15uerp3mehdxg33 --server-plan=basic
# env id 321が返却されれば、
$ aiopcli env get test
$ aiopcli env get 321
# が同じ結果を返却

# default endpointがmultipart/form-dataを受け取る場合
$ aiopcli predict test -Fimage=@invoice.png

# servableがapplication/jsonを受け取る場合
$ aiopcli predict 321 -d'{"inputs": {"array": [0, 4, 8]}}'

# 別のendpointを叩く
$ aiopcli predict 321 --endpoint=receipt/read -Fimage=@receipt.jpg

# apiコンテナログを抽出
$ aiopcli env logs 321
# 直近5分分のみ
$ aiopcli env logs 321 --since=5m
# 直近1分半分のみ
$ aiopcli env logs 321 --since=1m30s
# 推論コンテナのログ
$ aiopcli env logs 321 --container=triton-server

# この端末で登録されたenvを全て確認
$ aiopcli status

# envを削除
$ aiopcli delete test

# 推論サーバ（tritonserver, TF Servingなど）こみのコンテナイメージ登録
$ api_image=$(aiopcli image push api-server | jq -r .imageId)
$ inference_image=$(aiopcli image push inference-server | jq -r .imageId)
$ aiopcli servable create --name=my-image \
    --api-server=$api_image \
    --inference-server=$inference_image \
    --api-port=8000 \
    --metrics-port=8002 \  # tritonの場合のみ
    --liveness-endpoint=/health \
    --readiness-endpoint=/health/ready
```

## Usage guide

基本設定で作成
```
aiopcli create --servable=<servable-id> --server-plan=<basic,standard,gpu_basic>
```

tagを付けて作成
```
aiopcli create --tag=<tag> --servable=<servable-id> --server-plan=<basic,standard,gpu_basic>
```

環境を削除
```
aiopcli delete <tagまたはenv_id>
```

単体envのステータスを確認
```
aiopcli status <tagまたはenv_id>
```

cliで作成したenvのステータスを確認
```
aiopcli status
```

プロフィール（ホスト・APIキー）を設定してコマンドを実行
```
aiopcli --profile=<profile> <command> <arg> ...
# または
aiopcli -p<profile> <command> <arg> ...
```

host・apikeyをoverrideして実行
```
aiopcli --host=<host> --apikey=<apikey> <command> <arg> ...
# または
aiopcli --host=<host> -k<apikey> <command> <arg> ...
```

custom docker imageを登録
```
# イメージをプッシュ
image_id=$(aiopcli image push single-custom:develop | jq -r .imageId)

# apiserver
aiopcli servable create --name=single-custom \
    --api-server=$image_id \
    --api-port=8000 \
    --liveness-endpoint=/health \
    --readiness-endpoint=/health

# apiserver & inferenceserver
aiopcli servable create --name=double-custom \
  --api-server=API_IMAGE_ID \
  --inference-server=INFERENCE_IMAGE_ID
```

## Configuration

利用可能な環境変数
```
AIOP_CONFIG=~/.aiop
AIOP_LOG_LEVEL=INFO
AIOP_PROFILE=stg
AIOP_HOST=https://aiops.inside.ai
AIOP_APIKEY=ICMxJ0Z4PTtvbHE/ITd8Njk4RCgjcy5TL0E3b0YwRj83R2hXKTl8WFAiaGdpSU55fH0kd0IsOCJSZ1AwaUJuPVhWdFJvO1B0O09OQDtsOkVtPydKOnRaIUcqIm8ibFghWitiKTlxUVsqQWkkPG9lJFNbNyNrJzRoNTZzaTF7P2djMy9zKTg4JHZNMVEpQlBIayYkQTtRR2luOEIsXj1iO0JzRyJAdzBaVn1HbWNcc0k5X0JUO0tLeC1vdnRnNTVxLEJfbEEmR1lZNl97ZSZALl9FNnxDYSh+Q09WYHxDPEBqeWYhM1BUbDR5YEw0aCh3UlM6TnAxPmMhXzNnZ3YoYQ==
```

設定ファイルフォーマットはtoml。
デフォルト保存先： `~/.aiop`、`AIOP_CONFIG`環境変数で設定可。
```toml
# プロフィールのデフォルト
default = "stg"

# apikeyのデフォルト
apikey = "ICMxJ0Z4PTtvbHE/ITd8Njk4RCgjcy5TL0E3b0YwRj83R2hXKTl8WFAiaGdpSU55fH0kd0IsOCJSZ1AwaUJuPVhWdFJvO1B0O09OQDtsOkVtPydKOnRaIUcqIm8ibFghWitiKTlxUVsqQWkkPG9lJFNbNyNrJzRoNTZzaTF7P2djMy9zKTg4JHZNMVEpQlBIayYkQTtRR2luOEIsXj1iO0JzRyJAdzBaVn1HbWNcc0k5X0JUO0tLeC1vdnRnNTVxLEJfbEEmR1lZNl97ZSZALl9FNnxDYSh+Q09WYHxDPEBqeWYhM1BUbDR5YEw0aCh3UlM6TnAxPmMhXzNnZ3YoYQ=="

# profiles
[profiles.stg]
log_level = "INFO"

[profiles.prod]
apikey = "QDd+VC55cy1tLV4rQXo2bSZ1OXsgOnx0UzUwbDpEUEQ/UXc3cihvPmtBWHBTWj1LT1w+RXY/aCksbCthVUZGdFUzd2d6e1IrRi5zUycxKlp9YFxEdjE0PXNAXEtGVyZhOC14WWtcXXcoWls6OScxJmlkTSwrTDttc0ouIzhFLEZGJ3xFJWhpI3lpeV1iJ24nSjsyICcgRzxEIi95cGF0eU96TmheaWcobEk+RVxGX01ZYz9jfk9cbThIRyUpaXpLdDklJCR5eTVjYzwyb3F6J2pqJEZbckViNG16PHQkK3xqdUtBSjpRY1UoYiQ1MHBHLitYazUzKD52aVddXzYsbA=="
```
