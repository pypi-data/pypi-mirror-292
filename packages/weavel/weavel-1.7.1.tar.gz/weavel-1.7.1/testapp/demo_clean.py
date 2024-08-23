from weavel import Weavel
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

weavel = Weavel()

latencies = []

user_identifier = "TEST USER ID 0714"

session_id='TEST SESSION ID 0714'

# normal usage
session = weavel.session(user_id=user_identifier, session_id=session_id)

session.track(
    name="track_event_1",
    properties={"amount": "1 00"}
)

session.track(
    name="track_event_2"
)

session.message(
    role="user",
    content="Hi!",
)

session.trace(
    name="trace_1",
    inputs={"input_1": "input_1_value"},
    outputs={"output_1": "output_1_value"}
)

trace_id = "test_trace_id"
trace = session.trace(
    name="trace_2",
    record_id=trace_id
)

trace.span(
    name="span_1"
)

span = trace.span(
    name="span_2",
    inputs={"input_2": "input_2_value"},
    outputs={"output_2": "output_2_value"}
)

generation = span.generation(
    name="generation_1",
    inputs={"input_3": "input_3_value"},
    outputs={"output_3": "output_3_value"}
)

span_3 = span.span(
    name="span_3"
)

# update
span_3.update(
    inputs={"input_3": "input_3_value"},
    outputs={"output_3": "output_3_value"}
)
generation.update(
    inputs={"input_3": "input_3_new_value"},
)
trace.update(
    inputs={"input_4": "input_4_value"},
    outputs={"output_4": "output_4_value"}
)

# end
span_3.end()
generation.end()
span.end()
trace.end()

message = session.message(
    role="assistant",
    content="Hello!",
    metadata={"test_key": "test_value1"},
    ref_record_id=trace.record_id
)

# reuse session
session = weavel.session(session_id=session_id)

session.track(
    name="track_event_3",
    properties={"amount": "200"}
)

# reuse trace
trace = weavel.trace(
    record_id=trace_id
)

trace.log(
    name="log_1",
    value="log_1_value"
)

# create the new trace directly
trace_2 = weavel.trace(
    session_id=session_id,
    record_id="directly_created_trace_id",
    name="directly_created_trace",
)

trace_2.log(
    name="log_2",
    value="log_2_value"
)

previously_used_span_id = span.observation_id

# reuse span
span = weavel.span(
    observation_id=previously_used_span_id
)

span.log(
    name="log_3",
)

# create the new span directly
span_2 = weavel.span(
    record_id=trace.record_id,
    name="directly_created_span_2",
)

span_2.log(
    name="log_4",
)

# track directly

weavel.track(
    session_id=session_id,
    name="directly_created_track_1",
    properties={"amount": "300"}
)

weavel.close()
