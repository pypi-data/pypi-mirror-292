# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=broad-exception-caught
import json
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import List, Optional, Union
from ipulse_shared_base_ftredge import LogLevel
from .context_log import  ContextLog
############################################################################
##### PIPINEMON Collector for Logs and Statuses of running pipelines #######
class Pipelinemon:
    """A class for collecting logs and statuses of running pipelines.
    This class is designed to be used as a context manager, allowing logs to be
    collected, stored and reported in a structured format. The logs can be retrieved and
    analyzed at the end of the pipeline execution, or only the counts.
    """

    LEVELS_DIFF = 1000  # The difference in value between major log levels

    def __init__(self,  base_context: str, execution_domain:str, logger,
                 max_log_field_size:int =10000,
                 max_log_dict_size:float=256 * 1024 * 0.80,
                 max_log_traceback_lines:int = 30):
        self._id = str(uuid.uuid4())
        self._logs = []
        self._early_stop = False
        self._systems_impacted = []
        self._by_level_counts = {level.name: 0 for level in LogLevel}
        self._execution_domain = execution_domain
        self._base_context = base_context
        self._context_stack = []
        self._logger = logger
        self._max_log_field_size = max_log_field_size
        self._max_log_dict_size = max_log_dict_size
        self._max_log_traceback_lines = max_log_traceback_lines
        

    @contextmanager
    def context(self, context):
        self.push_context(context)
        try:
            yield
        finally:
            self.pop_context()

    def push_context(self, context):
        self._context_stack.append(context)

    def pop_context(self):
        if self._context_stack:
            self._context_stack.pop()

    @property
    def current_context(self):
        return " >> ".join(self._context_stack)

    @property
    def base_context(self):
        return self._base_context
    
    @base_context.setter
    def base_context(self, value):
        self._base_context = value

    @property
    def execution_domain(self):
        return self._execution_domain
    
    @execution_domain.setter
    def execution_domain(self, value):
        self._execution_domain = value

    @property
    def id(self):
        return self._id

    @property
    def systems_impacted(self):
        return self._systems_impacted

    @systems_impacted.setter
    def systems_impacted(self, list_of_si: List[str]):
        self._systems_impacted = list_of_si

    def add_system_impacted(self, system_impacted: str):
        if self._systems_impacted is None:
            self._systems_impacted = []
        self._systems_impacted.append(system_impacted)

    def clear_systems_impacted(self):
        self._systems_impacted = []

    @property
    def max_log_dict_size(self):
        return self._max_log_dict_size

    @max_log_dict_size.setter
    def max_log_dict_size(self, value):
        self._max_log_dict_size = value

    @property
    def max_log_field_size(self):
        return self._max_log_field_size

    @max_log_field_size.setter
    def max_log_field_size(self, value):
        self._max_log_field_size = value

    @property
    def max_log_traceback_lines(self):
        return self._max_log_traceback_lines

    @max_log_traceback_lines.setter
    def max_log_traceback_lines(self, value):
        self._max_log_traceback_lines = value

    @property
    def early_stop(self):
        return self._early_stop

    def set_early_stop(self, max_errors_tolerance:int=0, max_warnings_tolerance:int=0, create_error_log=True, pop_context=False):
        self._early_stop = True
        if create_error_log:
            if pop_context:
                self.pop_context()
            if max_errors_tolerance > 0:
                self.add_log(ContextLog(level=LogLevel.ERROR_PIPELINE_THRESHOLD_REACHED,
                                        subject="EARLY_STOP",
                                        description=f"Total MAX_ERRORS_TOLERANCE of {max_errors_tolerance} has been reached."))
            elif max_warnings_tolerance > 0:
                self.add_log(ContextLog(level=LogLevel.ERROR_PIPELINE_THRESHOLD_REACHED,
                                        subject="EARLY_STOP",
                                        description=f"Total MAX_WARNINGS_TOLERANCE of {max_warnings_tolerance} has been reached."))
            else:
                self.add_log(ContextLog(level=LogLevel.ERROR_PIPELINE_THRESHOLD_REACHED,
                                        subject="EARLY_STOP",
                                        description="Early stop has been triggered."))

    def reset_early_stop(self):
        self._early_stop = False


    def _update_counts(self, level: LogLevel, remove=False):
        """Updates the counts for the specified log level."""
        if remove:
            self._by_level_counts[level.name] -= 1
        else:
            self._by_level_counts[level.name] += 1

    def add_log(self, log: ContextLog ):
        log.base_context = self.base_context
        log.execution_domain = self.execution_domain
        log.context = self.current_context if self.current_context else "root"
        log.collector_id = self.id
        log.systems_impacted = self.systems_impacted
        log_dict = log.to_dict(max_field_len=self.max_log_field_size,
                               size_limit=self.max_log_dict_size,
                               max_traceback_lines=self.max_log_traceback_lines)
        self._logs.append(log_dict)
        self._update_counts(level=log.level)  # Pass the context to _update_counts

        if self._logger:
            # We specifically want to avoid having an ERROR log level for this structured Pipelinemon reporting, to ensure Errors are alerting on Critical Application Services.
            # A single ERROR log level is usually added at the end of the entire pipeline
            if log.level.value >= LogLevel.WARNING.value:
                self._logger.warning(log_dict)
            else:
                self._logger.info(log_dict)

    def add_logs(self, logs: List[ContextLog]):
        for log in logs:
            self.add_log(log)

    def clear_logs_and_counts(self):
        self._logs = []
        self._by_level_counts = {level.name: 0 for level in LogLevel}

    def clear_logs(self):
        self._logs = []

    def get_all_logs(self,in_json_format=False):
        if in_json_format:
            return json.dumps(self._logs)
        return self._logs

    def get_logs_for_level(self, level: LogLevel):
        return [log for log in self._logs if log["level_code"] == level.value]

    def get_logs_by_str_in_context(self, context_substring: str):
        return [
            log for log in self._logs
            if context_substring in log["context"]
        ]

    def _count_logs(self, context_string: str, exact_match=False,
                   levels: Optional[Union[LogLevel, List[LogLevel], range]] = None):
        """Counts logs based on context, exact match, and log levels.
        Args:
            context_string (str): The context string to match.
            exact_match (bool, optional): If True, matches the entire context string. 
                                       If False (default), matches context prefixes.
            levels (Optional[Union[LogLevel, List[LogLevel], range]], optional):
                - If None, counts all log levels.
                - If a single LogLevel, counts logs for that level.
                - If a list of LogLevels, counts logs for all levels in the list.
                - If a range object, counts logs with level values within that range. 
        """
        if levels is None:
            level_values = [level.value for level in LogLevel] # Count all levels
        elif isinstance(levels, LogLevel):
            level_values = [levels.value]
        elif isinstance(levels, range):
            level_values = list(levels)
        elif isinstance(levels, list) and all(isinstance(level, LogLevel) for level in levels):
            level_values = [level.value for level in levels]
        else:
            raise ValueError("Invalid 'levels' argument. Must be None, a LogLevel, a list of LogLevels, or a range.")

        return sum(
            1 for log in self._logs
            if (log["context"] == context_string if exact_match else log["context"].startswith(context_string)) and
               log["level_code"] in level_values
        )
    
    def count_logs_for_current_context(self, levels: Optional[Union[LogLevel, List[LogLevel], range]] = None):
        return self._count_logs(self.current_context, exact_match=True, levels=levels)

    def count_logs_for_current_and_nested_contexts(self, levels: Optional[Union[LogLevel, List[LogLevel], range]] = None):
        return self._count_logs(self.current_context, levels=levels)
    
    def count_errors(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.ERROR.value <= level.value < LogLevel.CRITICAL.value + self.LEVELS_DIFF)

    def count_errors_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.ERROR.value, LogLevel.CRITICAL.value + self.LEVELS_DIFF))

    def count_errors_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.ERROR.value, LogLevel.CRITICAL.value + self.LEVELS_DIFF))     
    
    def count_warnings_and_errors(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.WARNING.value <= level.value < LogLevel.CRITICAL.value + self.LEVELS_DIFF) 

    def count_warnings_and_errors_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.WARNING.value, LogLevel.CRITICAL.value + self.LEVELS_DIFF))

    def count_warnings_and_errors_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.WARNING.value, LogLevel.CRITICAL.value + self.LEVELS_DIFF))
    
    def count_warnings(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.WARNING.value <= level.value < LogLevel.WARNING.value + self.LEVELS_DIFF)

    def count_warnings_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.WARNING.value, LogLevel.WARNING.value + self.LEVELS_DIFF))

    def count_warnings_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.WARNING.value, LogLevel.WARNING.value + self.LEVELS_DIFF))        

    def count_actions(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.ACTION.value <= level.value < LogLevel.ACTION.value + self.LEVELS_DIFF)

    def count_actions_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.ACTION.value, LogLevel.ACTION.value + self.LEVELS_DIFF))

    def count_actions_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.ACTION.value, LogLevel.ACTION.value + self.LEVELS_DIFF))        

    def count_successes(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.SUCCESS.value <= level.value < LogLevel.SUCCESS.value + self.LEVELS_DIFF)

    def count_successes_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.SUCCESS.value, LogLevel.SUCCESS.value + self.LEVELS_DIFF))

    def count_successes_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.SUCCESS.value, LogLevel.SUCCESS.value + self.LEVELS_DIFF))        

    def count_notices(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.NOTICE.value <= level.value < LogLevel.NOTICE.value + self.LEVELS_DIFF)

    def count_notices_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.NOTICE.value, LogLevel.NOTICE.value + self.LEVELS_DIFF))

    def count_notices_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.NOTICE.value, LogLevel.NOTICE.value + self.LEVELS_DIFF))        

    def count_infos(self):
        return sum(self._by_level_counts.get(level.name, 0) for level in LogLevel if LogLevel.INFO.value <= level.value < LogLevel.INFO.value + self.LEVELS_DIFF)

    def count_infos_for_current_context(self):
        return self._count_logs(self.current_context, exact_match=True, levels=range(LogLevel.INFO.value, LogLevel.INFO.value + self.LEVELS_DIFF))

    def count_infos_for_current_and_nested_contexts(self):
        return self._count_logs(self.current_context, exact_match=False, levels=range(LogLevel.INFO.value, LogLevel.INFO.value + self.LEVELS_DIFF))  

    def generate_file_name(self, file_prefix=None, include_base_context=True):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        if not file_prefix:
            file_prefix = "pipelinelogs"
        if include_base_context:
            file_name = f"{file_prefix}_{timestamp}_{self.base_context}_len{len(self._logs)}.json"
        else:
            file_name = f"{file_prefix}_{timestamp}_len{len(self._logs)}.json"

        return file_name

    def import_logs_from_json(self, json_or_file, logger=None):
        def log_message(message):
            if logger:
                logger.info(message)

        def log_warning(message, exc_info=False):
            if logger:
                logger.warning(message, exc_info=exc_info)

        try:
            if isinstance(json_or_file, str):  # Load from string
                imported_logs = json.loads(json_or_file)
            elif hasattr(json_or_file, 'read'):  # Load from file-like object
                imported_logs = json.load(json_or_file)
            self.add_logs(imported_logs)
            log_message("Successfully imported logs from json.")
        except Exception as e:
            log_warning(f"Failed to import logs from json: {type(e).__name__} - {str(e)}", exc_info=True)


    def generate_final_log_message(self, subjectref: str, total_subjs: int) -> str:
        """Generates a final log message summarizing the pipeline execution."""

        message = f"""
        --------------------------------------------------
        Pipeline Execution Report
        --------------------------------------------------
        Base Context: {self.base_context}
        Execution Domain: {self.execution_domain}
        Pipeline ID: {self.id}
        Early Stop: {self.early_stop}
        --------------------------------------------------
        Results Summary:
        --------------------------------------------------
        - Successes: {self.count_successes()}/{total_subjs} {subjectref}(s)
            * With Notices: {self._by_level_counts[LogLevel.SUCCESS_WITH_NOTICES.name]}/{total_subjs} {subjectref}(s)
        - Actions: {self.count_actions()}
        - Notices: {self.count_notices()}
        - Warnings: {self.count_warnings()}
        - Errors: {self.count_errors()}
        - Infos: {self.count_infos()}
        --------------------------------------------------
        Detailed Breakdown:
        --------------------------------------------------"""

        # Add detailed breakdown for all levels with neat formatting
        for level in LogLevel:
            count = self._by_level_counts.get(level.name, 0)
            if count > 0:
                message += f"\n  - {level.name}: {count}"

        message += "\n--------------------------------------------------"
        return message

    def log_final_message(self, subjectref: str, total_subjs: int, generallogger):
        final_log_message = self.generate_final_log_message(subjectref=subjectref, total_subjs=total_subjs)
        if self.count_warnings_and_errors() > 0:
            generallogger.error(final_log_message)
        else:
            generallogger.info(final_log_message)
