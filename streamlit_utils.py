from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx

def get_session():
    session_id = get_script_run_ctx().session_id
    session_info = get_instance()._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't determine session_id")
    return id(session_info.session)