import os
import json

from api.app import create_app
from api.extensions import api as restx_api


def main(out_path: str = "documentation/api/openapi.json") -> None:
    app = create_app()
    # Build the OpenAPI schema under a request context so routes are registered
    with app.app_context():
        with app.test_request_context():
            spec = restx_api.__schema__
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate OpenAPI spec (JSON) for NeoV3 API")
    parser.add_argument("--out", default="documentation/api/openapi.json", help="Output file path")
    args = parser.parse_args()
    main(args.out)
