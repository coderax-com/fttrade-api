import logging

from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

from portfolio.utils.csv_ingestor import CsvIngestor


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load .csv file from ./data-source directory, parse and save to database.
    """
    help = "Load .csv file from ./data-source directory, parse and save to database."

    def handle(self, *args, **options):
        data_src_dir = settings.DATA_SOURCE_DIR
        csv_files = self._get_csv_files(data_src_dir)

        for csv_file in csv_files:
            log.info(f"Loading {csv_file} ...")
            ingestor = CsvIngestor()
            ingestor.load_csv_to_db(csv_file)
            log.info(f"Done")

    def _get_csv_files(self, dir: Path):
        files = sorted(dir.glob('*.csv'))
        return files