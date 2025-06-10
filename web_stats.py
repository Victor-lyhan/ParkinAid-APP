from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest
from google.oauth2 import service_account

# Path to your JSON key file
KEY_PATH = 'parkinaid-stats.json'
PROPERTY_ID = '483464546'

# Authenticate
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = BetaAnalyticsDataClient(credentials=credentials)


def get_view_count():
    request_users_by_country = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2025-01-01", end_date="today")]
    )

    response_users = client.run_report(request_users_by_country)
    total_view = 0
    for row in response_users.rows:
        # country = row.dimension_values[0].value
        # active_users = row.metric_values[0].value
        # print(f"{country}: {active_users}")
        total_view += int(row.metric_values[0].value)
    # print(f"People Impacted: {total_view}")
    return f"People Impacted: {total_view}"


def get_n_session():
    request_sessions_by_channel = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date="2025-01-01", end_date="today")]
    )

    response_sessions = client.run_report(request_sessions_by_channel)

    total_session = 0
    for row in response_sessions.rows:
        # channel = row.dimension_values[0].value
        # sessions = row.metric_values[0].value
        # print(f"{channel}: {sessions}")
        total_session += int(row.metric_values[0].value)
    # print(f"Analysis Ran: {total_session}")
    return f"Analysis Ran: {total_session}"


view_count = get_view_count()
session_count = get_n_session()
print(view_count)
print(session_count)
