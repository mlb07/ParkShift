from __future__ import annotations

import argparse

from parkshift.report import render_identity_report_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a standalone HTML report from ParkShift identity JSON."
    )
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-html", required=True)
    args = parser.parse_args()

    render_identity_report_file(args.input_json, args.output_html)
    print(f"Report: {args.output_html}")


if __name__ == "__main__":
    main()
