from profiler.advisor.config.config import Config
from profiler.advisor.utils.utils import Timer

Config().set_log_path(f"mstt_advisor_{Timer().strftime}.xlsx")
