import argparse
import asyncio
import json
import logging
import os
import sys
from app.reports.report import Report
from app.reports.report_engine import ReportEngine
from app.reports.report_lib import ReportInput


async def main():
    logging.basicConfig(
        stream=sys.stdout, format=" %(asctime)s:%(levelname)-8s:%(message)s"
    )
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.INFO)
    logger.info("Starting make")

    reports = await engine.make_reports(rep, args.api_key, args.api_url)
    for fmt, path in reports.items():
        # move the file path to the output name + format
        if fmt in args.formats.split(","):
            if "sample" in args.output_name:
                path.rename(f"{args.output_name}-{ri.report_id}.{fmt}")
            else:
                path.rename(f"{args.output_name}.{fmt}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate reports.")
    parser.add_argument(
        "--spec", type=str, help="Path to the report specification JSON file"
    )
    parser.add_argument(
        "--api_key", type=str, help="API key", default=os.getenv("PROD_API_KEY")
    )
    parser.add_argument(
        "--api_url", type=str, help="API URL", default="https://api.spyderbat.com"
    )
    parser.add_argument("--org", type=str, help="Organization")
    parser.add_argument(
        "-o", "--output_name", type=str, default="sample", help="Output name"
    )
    parser.add_argument(
        "--save_data",
        type=str,
        help="Only save the data to file, don't generate report",
    )

    parser.add_argument(
        "--formats",
        type=str,
        help="Comma separated list of formats to generate (default: json,yaml,md, mdx,html,pdf)",
        default="json,yaml,md,mdx,html,pdf",
    )

    args = parser.parse_args()

    with open(args.spec, "r") as f:
        report_input = json.load(f)
        report_input["org_uid"] = args.org
        ri = ReportInput.model_validate(report_input)
        rep = Report(input=ri, formats=["json", "yaml", "mdx", "html", "pdf"])

        engine = ReportEngine(
            {"backend": {"kind": "simple_file", "dir": "/tmp/reports"}}
        )
        if args.save_data:
            reporter = engine.get_reporter(ri.report_id)
            data = reporter.collector(
                args=ri.report_args,
                org_uid=ri.org_uid,
                api_key=args.api_key,
                api_url=args.api_url,
            )
            with open(args.save_data, "w") as f:
                for rec in data:
                    f.write(json.dumps(rec))
                    f.write("\n")
            exit(0)
        asyncio.run(main())
