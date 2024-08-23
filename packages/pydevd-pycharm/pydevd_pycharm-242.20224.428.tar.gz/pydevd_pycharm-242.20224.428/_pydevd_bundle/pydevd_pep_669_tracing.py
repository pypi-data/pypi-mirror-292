#  Copyright 2000-2024 JetBrains s.r.o. and contributors. Use of this source code is governed by the Apache 2.0 license.

import os
import sys
import threading
import traceback
from os.path import splitext, basename

from _pydev_bundle import pydev_log
from _pydev_bundle.pydev_is_thread_alive import is_thread_alive
from _pydevd_bundle.pydevd_breakpoints import stop_on_unhandled_exception
from _pydevd_bundle.pydevd_bytecode_utils import (
    find_last_call_name, find_last_func_call_order)
from _pydevd_bundle.pydevd_comm_constants import (
    CMD_STEP_OVER, CMD_SMART_STEP_INTO, CMD_SET_BREAK, CMD_STEP_INTO,
    CMD_STEP_INTO_MY_CODE, CMD_STEP_INTO_COROUTINE, CMD_STEP_RETURN)
from _pydevd_bundle.pydevd_constants import (
    PYDEVD_TOOL_NAME, STATE_RUN, STATE_SUSPEND, GlobalDebuggerHolder)
from _pydevd_bundle.pydevd_dont_trace_files import DONT_TRACE, PYDEV_FILE
from _pydevd_bundle.pydevd_trace_dispatch import (
    set_additional_thread_info, handle_breakpoint_condition,
    handle_breakpoint_expression, DEBUG_START, DEBUG_START_PY3K,
    should_stop_on_exception, handle_exception, manage_return_values)
from pydevd_file_utils import (
    NORM_PATHS_AND_BASE_CONTAINER, get_abs_path_real_path_and_base_from_frame)

get_current_thread = threading.current_thread
get_file_type = DONT_TRACE.get

global_cache_skips = {}
global_cache_frame_skips = {}


try:
    monitoring = sys.monitoring
except AttributeError:
    pass


def _make_frame_cache_key(code):
    return code.co_firstlineno, code.co_name, code.co_filename


def _get_additional_info(thread):
    try:
        additional_info = thread.additional_info
        if additional_info is None:
            raise AttributeError()
    except:
        additional_info = set_additional_thread_info(thread)
    return additional_info


def _get_abs_path_real_path_and_base_from_frame(frame):
    try:
        abs_path_real_path_and_base = NORM_PATHS_AND_BASE_CONTAINER[
            frame.f_code.co_filename]
    except:
        abs_path_real_path_and_base \
            = get_abs_path_real_path_and_base_from_frame(frame)

    return abs_path_real_path_and_base


def _should_enable_line_events_for_code(frame, code, filename, info):
    line_number = frame.f_lineno

    # print('PY_START (should enable line events check) %s %s %s %s' % (line_number, code.co_name, filename, info.pydev_step_cmd))

    py_db = GlobalDebuggerHolder.global_dbg

    plugin_manager = py_db.plugin

    stop_frame = info.pydev_step_stop
    step_cmd = info.pydev_step_cmd

    breakpoints_for_file = py_db.breakpoints.get(filename)

    can_skip = False

    if info.pydev_state == 1:  # STATE_RUN = 1
        can_skip = (step_cmd == -1 and stop_frame is None) \
                   or (step_cmd in (109, 108) and stop_frame is not frame)

        if can_skip:
            if plugin_manager is not None and py_db.has_plugin_line_breaks:
                can_skip = not plugin_manager.can_not_skip(
                    py_db, frame, info)

            # CMD_STEP_OVER = 108
            if (can_skip and py_db.show_return_values
                    and info.pydev_step_cmd == 108
                    and frame.f_back is info.pydev_step_stop):
                # trace function for showing return values after step over
                can_skip = False

    frame_cache_key = _make_frame_cache_key(code)
    line_cache_key = (frame_cache_key, line_number)

    if breakpoints_for_file:
        if can_skip:
            # When cached, 0 means we don't have a breakpoint
            # and 1 means we have.
            breakpoints_in_line_cache = global_cache_frame_skips.get(
                line_cache_key, -1)
            if breakpoints_in_line_cache == 0:
                return False

            breakpoints_in_frame_cache = global_cache_frame_skips.get(
                frame_cache_key, -1)
            if breakpoints_in_frame_cache != -1:
                has_breakpoint_in_frame = breakpoints_in_frame_cache == 1
            else:
                has_breakpoint_in_frame = False
                # Checks the breakpoint to see if there is a context
                # match in some function.
                curr_func_name = frame.f_code.co_name

                # global context is set with an empty name
                if curr_func_name in ('?', '<module>', '<lambda>'):
                    curr_func_name = ''

                for breakpoint in breakpoints_for_file.values():
                    # will match either global or some function
                    if breakpoint.func_name in ('None', curr_func_name):
                        has_breakpoint_in_frame = True
                        break

                # Cache the value (1 or 0 or -1 for default because of cython).
                if has_breakpoint_in_frame:
                    global_cache_frame_skips[frame_cache_key] = 1
                else:
                    global_cache_frame_skips[frame_cache_key] = 0

            if can_skip and not has_breakpoint_in_frame:
                return False

    return True


def _clear_run_state(info):
    info.pydev_step_stop = None
    info.pydev_step_cmd = -1
    info.pydev_state = STATE_RUN

# Cythonnized functions live in C the call stack rather than in the Python call stack.
# It means that the function gets its Python caller's stack frame at depth 0, and
# not its own.
# This behavior should be treated as undefined, and can be changed on the
# Cython side in the future.
# IFDEF CYTHON
# cdef _getframe(depth=0):
#    return sys._getframe()
# ELSE
_getframe = sys._getframe
# ENDIF


def _get_top_level_frame():
    f_unhandled = _getframe()

    while f_unhandled:
        filename = f_unhandled.f_code.co_filename
        name = splitext(basename(filename))[0]
        if name == 'pydevd':
            if f_unhandled.f_code.co_name == '_exec':
                break
        elif name == 'threading':
            if f_unhandled.f_code.co_name == '_bootstrap_inner':
                break
        f_unhandled = f_unhandled.f_back

    return f_unhandled


def _stop_on_unhandled_exception(exc_info, py_db, thread):
    additional_info = _get_additional_info(thread)
    if not additional_info.suspended_at_unhandled:
        additional_info.suspended_at_unhandled = True
        stop_on_unhandled_exception(py_db, thread, additional_info,
                                    exc_info)


def enable_pep669_monitoring():
    DEBUGGER_ID = monitoring.DEBUGGER_ID
    if not monitoring.get_tool(DEBUGGER_ID):
        monitoring.use_tool_id(DEBUGGER_ID, PYDEVD_TOOL_NAME)

        monitoring.set_events(
            DEBUGGER_ID,
            monitoring.events.PY_START | monitoring.events.RAISE
        )

        for event_type, callback in (
            (monitoring.events.PY_START, py_start_callback),
            (monitoring.events.LINE, py_line_callback),
            (monitoring.events.PY_RETURN, py_return_callback),
            (monitoring.events.RAISE, py_raise_callback),
        ):
            monitoring.register_callback(DEBUGGER_ID, event_type, callback)

    debugger = GlobalDebuggerHolder.global_dbg
    if debugger:
        debugger.is_pep669_monitoring_enabled = True


def _enable_return_tracing(code):
    local_events = monitoring.get_local_events(monitoring.DEBUGGER_ID, code)
    monitoring.set_local_events(monitoring.DEBUGGER_ID, code,
                                local_events | monitoring.events.PY_RETURN)


def _enable_line_tracing(code):
    local_events = monitoring.get_local_events(monitoring.DEBUGGER_ID, code)
    monitoring.set_local_events(monitoring.DEBUGGER_ID, code,
                                local_events | monitoring.events.LINE)


def py_start_callback(code, instruction_offset):
    try:
        py_db = GlobalDebuggerHolder.global_dbg
    except AttributeError:
        return

    if py_db is None:
        return monitoring.DISABLE

    frame = _getframe(1)

    # print('ENTER: PY_START ', code.co_filename, frame.f_lineno, code.co_name)

    try:
        if py_db._finish_debugging_session:
            return monitoring.DISABLE

        thread = get_current_thread()

        if not is_thread_alive(thread):
            return

        if py_db.thread_analyser is not None:
            py_db.thread_analyser.log_event(frame)

        if py_db.asyncio_analyser is not None:
            py_db.asyncio_analyser.log_event(frame)

        frame_cache_key = _make_frame_cache_key(code)

        info = _get_additional_info(thread)
        pydev_step_cmd = info.pydev_step_cmd
        is_stepping = pydev_step_cmd != -1

        if not is_stepping and frame_cache_key in global_cache_skips:
            # print('skipped: PY_START (cache hit)', frame_cache_key, frame.f_lineno, code.co_name)
            return monitoring.DISABLE

        abs_path_real_path_and_base = _get_abs_path_real_path_and_base_from_frame(frame)
        filename = abs_path_real_path_and_base[1]
        file_type = get_file_type(abs_path_real_path_and_base[-1])

        if file_type is not None:
            if file_type == 1:  # inlining LIB_FILE = 1
                if not py_db.in_project_scope(filename):
                    # print('skipped: PY_START (not in scope)', abs_path_real_path_and_base[-1], frame.f_lineno, code.co_name, file_type)
                    global_cache_skips[frame_cache_key] = 1
                    return monitoring.DISABLE
            else:
                # print('skipped: PY_START', abs_path_real_path_and_base[-1], frame.f_lineno, code.co_name, file_type)
                global_cache_skips[frame_cache_key] = 1
                return monitoring.DISABLE

        breakpoints_for_file = (py_db.breakpoints.get(filename)
                                or py_db.has_plugin_line_breaks)
        if not breakpoints_for_file and not is_stepping:
            return monitoring.DISABLE

        if py_db.plugin and py_db.has_plugin_line_breaks:
            args = (py_db, filename, info, thread)
            result = py_db.plugin.get_breakpoint(py_db, frame, 'call', args)
            if result is not None:
                flag, breakpoint, new_frame, bp_type = result
                if breakpoint:
                    eval_result = False
                    if breakpoint.has_condition:
                        eval_result = handle_breakpoint_condition(py_db, info, breakpoint, new_frame)

                    if breakpoint.expression is not None:
                        handle_breakpoint_expression(breakpoint, info, new_frame)
                        if breakpoint.is_logpoint and info.pydev_message is not None and len(
                                info.pydev_message) > 0:
                            cmd = py_db.cmd_factory.make_io_message(info.pydev_message + os.linesep, '1')
                            py_db.writer.add_command(cmd)

                    if breakpoint.has_condition and not eval_result:
                        return

                if flag:
                    result = py_db.plugin.suspend(py_db, thread, frame, bp_type)
                    if result is not None:
                        frame = result

                if info.pydev_state == STATE_SUSPEND:
                    py_db.do_wait_suspend(thread, frame, 'call', None)
                    return

        if is_stepping:
            if (pydev_step_cmd == CMD_STEP_OVER
                    and frame is not info.pydev_step_stop):
                if frame.f_back is info.pydev_step_stop:
                    _enable_return_tracing(code)
            if (py_db.is_filter_enabled
                    and py_db.is_ignored_by_filters(filename)):
                return monitoring.DISABLE
            if (py_db.is_filter_libraries
                    and not py_db.in_project_scope(filename)):
                return monitoring.DISABLE
            # We are stepping, and there is no reason to skip the frame
            # at this point.
            _enable_line_tracing(code)
            _enable_return_tracing(code)

            # Process plugins stepping
            stop_info = {}
            args = (py_db, filename, info, thread)
            stop_frame = info.pydev_step_stop
            plugin_stop = False

            if py_db.plugin is not None:
                if pydev_step_cmd == CMD_STEP_INTO:
                    result = py_db.plugin.cmd_step_into(py_db, frame, 'call', args, stop_info, False)
                    if result:
                        _, plugin_stop = result
                if pydev_step_cmd == CMD_STEP_OVER:
                    result = py_db.plugin.cmd_step_over(py_db, frame, 'call', args, stop_info, stop_frame is frame)
                    if result:
                        _, plugin_stop = result

            if plugin_stop:
                py_db.plugin.stop(py_db, frame, 'call', args, stop_info, None, pydev_step_cmd)

        if _should_enable_line_events_for_code(frame, code, filename, info):
            _enable_line_tracing(code)
            _enable_return_tracing(code)
        else:
            global_cache_skips[frame_cache_key] = 1
            return monitoring.DISABLE

    except SystemExit:
        return monitoring.DISABLE
    except Exception:
        try:
            if traceback is not None:
                traceback.print_exc()
        except:
            pass
        return monitoring.DISABLE


def py_line_callback(code, line_number):
    frame = _getframe(1)
    thread = get_current_thread()
    info = _get_additional_info(thread)

    # print('LINE %s %s %s %s' % (frame.f_lineno, code.co_name, code.co_filename, info.pydev_step_cmd))

    if info.is_tracing:
        return

    try:
        info.is_tracing = True

        py_db = GlobalDebuggerHolder.global_dbg

        if py_db._finish_debugging_session:
            return monitoring.DISABLE

        stop_frame = info.pydev_step_stop
        step_cmd = info.pydev_step_cmd

        filename = _get_abs_path_real_path_and_base_from_frame(frame)[1]
        breakpoints_for_file = py_db.breakpoints.get(filename)

        frame_cache_key = _make_frame_cache_key(code)
        line_cache_key = (frame_cache_key, line_number)

        try:
            flag = False
            breakpoint = None
            stop = False
            exist_result = False
            bp_type = None
            args = (py_db, filename, info, thread)
            new_frame = frame
            smart_stop_frame = info.pydev_smart_step_context.smart_step_stop
            context_start_line = info.pydev_smart_step_context.start_line
            context_end_line = info.pydev_smart_step_context.end_line
            is_within_context = (context_start_line <= line_number
                                 <= context_end_line)

            if breakpoints_for_file and line_number in breakpoints_for_file:
                breakpoint = breakpoints_for_file[line_number]
                stop = True
                if step_cmd == CMD_STEP_OVER:
                    if stop_frame is frame:
                        stop = False
                    elif step_cmd == CMD_SMART_STEP_INTO and (
                            frame.f_back is smart_stop_frame and is_within_context):
                        stop = False
            elif py_db.plugin is not None and py_db.has_plugin_line_breaks:
                result = py_db.plugin.get_breakpoint(py_db, frame, 'line', args)
                if result:
                    exist_result = True
                    flag, breakpoint, new_frame, bp_type = result

            if breakpoint:
                if stop or exist_result:
                    eval_result = False
                    if breakpoint.has_condition:
                        eval_result = handle_breakpoint_condition(py_db, info, breakpoint, new_frame)

                    if breakpoint.expression is not None:
                        handle_breakpoint_expression(breakpoint, info, new_frame)
                        if breakpoint.is_logpoint and info.pydev_message is not None and len(
                                info.pydev_message) > 0:
                            cmd = py_db.cmd_factory.make_io_message(info.pydev_message + os.linesep, '1')
                            py_db.writer.add_command(cmd)

                    if breakpoint.has_condition and not eval_result:
                        return
            else:
                if step_cmd != -1:
                    if (py_db.is_filter_enabled
                            and py_db.is_ignored_by_filters(filename)):
                        # ignore files matching stepping filters
                        return monitoring.DISABLE
                    if (py_db.is_filter_libraries
                            and not py_db.in_project_scope(filename)):
                        # ignore library files while stepping
                        return monitoring.DISABLE

            if stop:
                py_db.set_suspend(
                    thread,
                    CMD_SET_BREAK,
                    suspend_other_threads=breakpoint
                                          and breakpoint.suspend_policy == "ALL",
                )
            elif flag and py_db.plugin is not None:
                result = py_db.plugin.suspend(py_db, thread, frame, bp_type)
                if result:
                    frame = result

            # if thread has a suspend flag, we suspend with a busy wait
            if info.pydev_state == STATE_SUSPEND:
                py_db.do_wait_suspend(thread, frame, 'line', None)
            elif not breakpoint:
                # No stop from anyone and no breakpoint found in line (cache that).
                global_cache_frame_skips[line_cache_key] = 0
        except KeyboardInterrupt:
            _clear_run_state(info)
            raise
        except:
            traceback.print_exc()
            raise

        # Step handling. We stop when we hit the right frame.
        try:
            plugin_stop = False
            args = (py_db, filename, info, thread)
            stop_info = {}
            stop = False

            if step_cmd == CMD_SMART_STEP_INTO:
                if smart_stop_frame is frame and not is_within_context:
                        # We don't stop on jumps in multiline statements, which
                        # the Python interpreter does in some cases, if we they
                        # happen in smart step into context.
                        info.pydev_func_name = '.invalid.'  # Must match the type in cython
                        stop = True  # act as if we did a step into

                curr_func_name = frame.f_code.co_name

                if curr_func_name in ('?', '<module>') or curr_func_name is None:
                    curr_func_name = ''

                if smart_stop_frame and smart_stop_frame is frame.f_back:
                    try:
                        if curr_func_name != info.pydev_func_name and frame.f_back:
                            # try to find function call name using bytecode analysis
                            curr_func_name = find_last_call_name(frame.f_back)
                        if curr_func_name == info.pydev_func_name:
                            stop = (find_last_func_call_order(
                                frame.f_back, context_start_line)
                                    == info.pydev_smart_step_context.call_order)
                    except:
                        pydev_log.debug("Exception while handling smart step into "
                                        "in frame tracer, step into will be "
                                        "performed instead.")
                        info.pydev_smart_step_context.reset()
                        stop = True  # act as if we did a step into

            elif step_cmd == CMD_STEP_INTO:
                stop = True
                if py_db.plugin is not None:
                    result = py_db.plugin.cmd_step_into(py_db, frame, 'line', args, stop_info, stop)
                    if result:
                        stop, plugin_stop = result

            elif step_cmd == CMD_STEP_INTO_MY_CODE:
                stop = py_db.in_project_scope(frame.f_code.co_filename)

            elif step_cmd in (CMD_STEP_OVER, CMD_STEP_INTO_COROUTINE):
                stop = stop_frame is frame
                if stop:
                    # The only case we shouldn't stop on a line, is when
                    # we are traversing though asynchronous framework machinery
                    if step_cmd == CMD_STEP_INTO_COROUTINE:
                        stop = py_db.in_project_scope(frame.f_code.co_filename)

                if step_cmd == CMD_STEP_OVER and py_db.plugin is not None:
                    result = py_db.plugin.cmd_step_over(py_db, frame, 'line', args, stop_info, stop)
                    if result:
                        stop, plugin_stop = result

            if plugin_stop:
                py_db.plugin.stop(py_db, frame, 'line', args, stop_info, None, step_cmd)
            elif stop:
                py_db.set_suspend(thread, step_cmd)
                py_db.do_wait_suspend(thread, frame, 'line', None)

        except KeyboardInterrupt:
            _clear_run_state(info)
            raise
        except:
            traceback.print_exc()
            raise

    finally:
        info.is_tracing = False


def py_raise_callback(code, instruction_offset, exception):
    # print('PY_RAISE %s %s %s' % (code.co_name, code.co_filename, exception))

    exc_info = (type(exception), exception, exception.__traceback__)

    try:
        py_db = GlobalDebuggerHolder.global_dbg
    except AttributeError:
        py_db = None

    if py_db is None:
        return

    thread = get_current_thread()
    info = _get_additional_info(thread)

    try:
        frame = _getframe(1)
        if frame is _get_top_level_frame():
            _stop_on_unhandled_exception(exc_info, py_db, thread)
            return

        has_exception_breakpoints = (py_db.break_on_caught_exceptions
                                     or py_db.has_plugin_exception_breaks
                                     or py_db.stop_on_failed_tests)
        if has_exception_breakpoints:
            args = (
                py_db,
                _get_abs_path_real_path_and_base_from_frame(frame)[1],
                info, thread,
                global_cache_skips,
                global_cache_frame_skips
            )
            should_stop, frame = should_stop_on_exception(
                args, frame, 'exception', exc_info)
            if should_stop:
                handle_exception(args, frame, 'exception', exc_info)
    except KeyboardInterrupt:
        _clear_run_state(info)
        raise


def py_return_callback(code, instruction_offset, retval):
    # print('PY_RETURN %s %s %s' % (code, code.co_name, code.co_filename))
    try:
        py_db = GlobalDebuggerHolder.global_dbg
    except AttributeError:
        py_db = None

    if py_db is None:
        return monitoring.DISABLE

    frame = _getframe(1)
    thread = get_current_thread()
    info = _get_additional_info(thread)
    stop_frame = info.pydev_step_stop
    filename = _get_abs_path_real_path_and_base_from_frame(frame)[1]
    plugin_stop = False
    args = (py_db, filename, info, thread)
    stop_info = {}
    stop = False

    try:
        if py_db.show_return_values or py_db.remove_return_values_flag:
            manage_return_values(py_db, frame, 'return', retval)

        step_cmd = info.pydev_step_cmd

        if step_cmd == CMD_STEP_INTO and py_db.plugin is not None:
            result = py_db.plugin.cmd_step_into(py_db, frame, 'return', args, stop_info, True)
            if result:
                stop, plugin_stop = result

        elif step_cmd in (CMD_STEP_OVER, CMD_STEP_RETURN):
            stop = stop_frame is frame
            if stop:
                stop = frame.f_back and py_db.in_project_scope(frame.f_back.f_code.co_filename)
                if not stop:
                    if frame.f_back:
                        back = frame.f_back
                        info.pydev_step_stop = back
                        back_code = back.f_code
                        if not py_db.in_project_scope(back_code.co_filename):
                            stop = not step_cmd == CMD_STEP_INTO_COROUTINE

                    else:
                        # if there's no back frame, we just stop as soon as possible
                        info.pydev_step_cmd = CMD_STEP_INTO
                        info.pydev_step_stop = None

            if step_cmd == CMD_STEP_OVER and py_db.plugin is not None:
                result = py_db.plugin.cmd_step_over(py_db, frame, 'return', args, stop_info, stop)
                if result:
                    stop, plugin_stop = result

        if stop and step_cmd != -1 and hasattr(frame, "f_back"):
            f_code = getattr(frame.f_back, 'f_code', None)
            if f_code is not None:
                back_filename = os.path.basename(f_code.co_filename)
                file_type = get_file_type(back_filename)
                if file_type == PYDEV_FILE:
                    stop = False

        if plugin_stop:
            py_db.plugin.stop(py_db, frame, 'return', args, stop_info, None, step_cmd)
        elif stop:
            back = frame.f_back
            if back is not None:
                _, back_filename, base = get_abs_path_real_path_and_base_from_frame(back)
                if (base, back.f_code.co_name) in (DEBUG_START, DEBUG_START_PY3K):
                    back = None

            if back is not None:
                # if we're in a return, we want it to appear to the user in the previous frame!
                py_db.set_suspend(thread, step_cmd)
                py_db.do_wait_suspend(thread, back, 'return', retval)
    except KeyboardInterrupt:
        _clear_run_state(info)
        raise
    finally:
        return monitoring.DISABLE
