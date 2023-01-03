from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.monitors.mixins import StatsMonitorMixin
from spidermon.contrib.actions.reports.files import CreateFileReport

@monitors.name('Item count')
class ItemCountMonitor(Monitor):

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = 10

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name('Item validation')
class ItemValidationMonitor(Monitor, StatsMonitorMixin):

    @monitors.name('No item validation errors')
    def test_no_item_validation_errors(self):
        validation_errors = getattr(
            self.stats, 'spidermon/validation/fields/errors', 0
        )
        self.assertEqual(
            validation_errors,
            0,
            msg='Found validation errors in {} fields'.format(
                validation_errors)
        )


@monitors.name("History Validation")
class HistoryMonitor(Monitor):
    @monitors.name("Expected number of items extracted")
    def test_expected_number_of_items_extracted(self):
        spider = self.data["spider"]
        total_previous_jobs = len(spider.stats_history)
        if total_previous_jobs == 0:
            return

        previous_item_extracted_mean = (
            sum(previous_job["item_scraped_count"] for previous_job in spider.stats_history)/ total_previous_jobs)
        items_extracted = self.data.stats["item_scraped_count"]

        # Minimum number of items we expect to be extracted
        minimum_threshold = 0.9 * previous_item_extracted_mean

        self.assertFalse(items_extracted <= minimum_threshold, msg="Expected at least {} items extracted.".format(minimum_threshold))

class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        ItemCountMonitor,
        ItemValidationMonitor,
        HistoryMonitor,
    ]

    monitors_finished_actions =[
        CreateFileReport
    ]