from pathlib import Path
from typing import List, Optional
import contextlib
import json
import http
import re
import sys


def handle_response(response, stream=False):
    status = 0
    if not (200 <= response.status_code < 300):
        status_tag = http.HTTPStatus(response.status_code).phrase
        print(f"Error: {response.status_code} {status_tag}", file=sys.stderr)
        if stream:
            # response.content doesn't exist in this case until read
            response.read()
        if response.content:
            print(response.content.decode(), file=sys.stderr)
        status = 1
    else:
        if stream:
            for line in response.iter_lines():
                if line:
                    print(line, flush=True)
        else:
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except Exception:
                print(response.text)
    return status


@contextlib.contextmanager
def prepare_fields(fields: Optional[List[str]], data: Optional[str]):
    if fields and data:
        raise ValueError("Cannot specify both --form and --data")
    if data:
        yield None, data
    else:
        files = {}
        data = {}
        with contextlib.ExitStack() as stack:
            for field in fields:
                try:
                    key, value = field.split('=', 1)
                except ValueError:
                    raise ValueError(
                        f"Invalid field format: '{field}'. "
                        f"Expected: <key>=<string> or <key>=@<path>"
                    )
                if value.startswith('@'):
                    path = value[1:]
                    value = (path, stack.enter_context(Path(path).open('rb')))
                    files[key] = value
                else:
                    data[key] = value
            yield files or None, data or None


def is_tar_gzip_file(s):
    return re.search(r'\.(t|tar\.)gz$', s)


def is_image_id(s):
    return re.search(r'^i-[a-z0-9]{16}$', s)
