# app/utils/case_state.py

user_sessions = {}

def set_user_case_session(user_id, session):
    user_sessions[user_id] = session

def get_user_case_session(user_id):
    return user_sessions.get(user_id)

def is_user_in_case(user_id):
    return user_id in user_sessions