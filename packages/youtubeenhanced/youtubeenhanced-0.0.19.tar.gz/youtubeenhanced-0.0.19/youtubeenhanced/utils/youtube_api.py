from yta_general_utils.file_processor import get_project_abspath

API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_SECRET_FILENAME = get_project_abspath() + 'client-secret.json'
TOKEN_FILES_ABSPATH = get_project_abspath() + 'token_files/'

def is_youtube_token_valid():
    """
    Checks if the current Youtube Data v3 API token is valid.

    This method returns True if yes, or False if not.
    """
    from yta_google_api.oauth.google_oauth_api import GoogleOauthAPI

    return GoogleOauthAPI(CLIENT_SECRET_FILENAME, TOKEN_FILES_ABSPATH).is_oauth_token_valid(API_NAME, API_VERSION, SCOPES)

def start_youtube_auth_flow():
    """
    Starts the Google auth flow for Youtube Data v3 API.
    """
    from youtubeenhanced.utils.google_oauth_api import GoogleOauthAPI

    return GoogleOauthAPI(CLIENT_SECRET_FILENAME, TOKEN_FILES_ABSPATH).start_google_auth_flow(API_NAME, API_VERSION, SCOPES)

def create_youtube_service():
    """
    Creates a Youtube Data v3 API service and returns it.
    """
    from youtubeenhanced.utils.google_oauth_api import GoogleOauthAPI

    return GoogleOauthAPI(CLIENT_SECRET_FILENAME, TOKEN_FILES_ABSPATH).create_service(API_NAME, API_VERSION, SCOPES)
