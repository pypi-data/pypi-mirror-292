from weavel import Weavel
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

start_time = datetime.now()
weavel = Weavel()
start_latency = (datetime.now() - start_time).total_seconds()
print("Start latency: ", start_latency)

latencies = []

user_identifier = "TEST USER ID 0630"

session_id='TEST SESSION ID 0630'
start_time = datetime.now()
session = weavel.session(user_id=user_identifier, session_id=session_id)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
session.track_event(
    name="paid",
    properties={"amount": "100"}
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
session.track_event(
    name="test"
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
session.message(
    role="user",
    content="Hi!",
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
trace = session.trace(
    name="retrieval",
    record_id="test_trace_id"
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
trace.log(
    name="DB-1"
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
span = trace.span(
    name="search_engine"
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
span.log(
    name="query",
    value="AAA"
)
latencies.append((datetime.now() - start_time).total_seconds())

start_time = datetime.now()
message = session.message(
    role="assistant",
    content="Hello!",
    metadata={"test_key": "test_value1"},
    reason_record_id=trace.record_id
)
latencies.append((datetime.now() - start_time).total_seconds())

for latency in latencies:
    print(latency)

# mean latency
print(sum(latencies) / len(latencies))

weavel.identify(
    user_id=user_identifier,
    properties={"name": "AAAA"}
)

start_time = datetime.now()
weavel.close()
final_latency = (datetime.now() - start_time).total_seconds()
print("Final latency: ", final_latency)