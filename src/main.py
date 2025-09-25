import asyncio
import logging
import sys

from .config import settings
from .elt.extract import extract_data_from_files
from .elt.load import export_report_to_csv, generate_report_stdout
from .elt.transform import transform_minion_data
from .logging import setup_logging
from .services.service_gateway import ServiceGateway


async def main():
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("Application starting.")

    json_files = list(settings.paths.data_dir.glob("*.json"))
    if not json_files:
        print(
            f"Error: No JSON files found in directory: {settings.paths.data_dir}",
            file=sys.stderr,
        )
        return

    print(f"Found {len(json_files)} files to process in '{settings.paths.data_dir}'...")

    all_minion_data = extract_data_from_files(json_files)
    if not any(all_minion_data):
        print(
            "Error: No minion data could be successfully processed from any file.",
            file=sys.stderr,
        )
        return

    processed_data = transform_minion_data(
        settings.salt.target_version,
        all_minion_data,
    )

    for file_path, (updatable, higher, unresponsive) in zip(json_files, processed_data):
        report_title = file_path.name
        generate_report_stdout(report_title, updatable, higher, unresponsive)

        export_report_to_csv(
            report_title, updatable, higher, unresponsive, settings.paths.reports_dir
        )

    try:
        gateway = ServiceGateway(settings)

        log.info("Requesting service data bundle from gateway.")
        service_data = await gateway.get_all_service_data(salt_target="*")
        minion_count = len(service_data.salt.return_data[0].root)
        log.info(f"Gateway returned data for {minion_count} minions.")

        for minion_id, grains in service_data.salt.return_data[0].root.items():
            print(f"OS for {minion_id}: {grains.osfinger}")

    except Exception:
        log.exception("An unhandled exception occurred in the main application.")

    log.info("Application finished.")


if __name__ == "__main__":
    asyncio.run(main())
