from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry import trace, context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import httpx
from loguru import logger
from typing import  Optional
from opentelemetry.trace import Span
from uuid import UUID

class CustomHTTPXClientInstrumentor(HTTPXClientInstrumentor):
    def __init__(self, tracer=None):
        super().__init__()
        self._original_send = None
        self._propagator = TraceContextTextMapPropagator()
        self._tracer = tracer or trace.get_tracer(__name__)

    def _instrument(self, **kwargs):
        logger.info("ABHI init")
        super()._instrument(**kwargs)
        self._original_send = httpx.Client.send

        def instrumented_send(client, request, **kwargs):
            current_context = context.get_current()
            current_span = trace.get_current_span(current_context)
            logger.info(f"\n Request is {request} and \n args {kwargs}\n")
            tracer = trace.get_tracer(__name__)
            logger.info(f"\n tracer {self._tracer}, Current CONTEXT is  --> {current_span} \n")
            with self._tracer.start_as_current_span(
                f"HTTP {request.method}",
                context=trace.set_span_in_context(current_span),
                kind=trace.SpanKind.CLIENT,
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                },
            ) as span:
                # Inject the current context into the headers
                self._propagator.inject(request.headers)

                # Add custom trace IDs
                if span.is_recording():
                    span_context = span.get_span_context()
                    trace_id = format(span_context.trace_id, '032x')
                    span_id = format(span_context.span_id, '016x')
                    request.headers['X-Custom-Trace-ID'] = trace_id
                    request.headers['X-Custom-Span-ID'] = span_id

                # Log the headers for inspection
                logger.info(f"Outgoing request headers: {request.headers} \n")

                try:
                    response = self._original_send(client, request, **kwargs)
                    logger.info(f"\n response {response}")
                    span.set_attribute("http.status_code", response.status_code)
                    return response
                except Exception as e:
                    span.record_exception(e)
                    raise
            # current_context = trace.get_current_span().get_span_context()
            # logger.info"\n Current context is  -->", current_context)
            # # Inject the current context into the headers
            # self._propagator.inject(request.headers)

            # # Add custom trace IDs
            # if current_context.is_valid:
            #     trace_id = format(current_context.trace_id, '032x')
            #     span_id = format(current_context.span_id, '016x')
            #     request.headers['X-Custom-Trace-ID'] = trace_id
            #     request.headers['X-Custom-Span-ID'] = span_id

            # # Log the headers for inspection
            # logger.info"CustomHTTPXClientInstrumentor Outgoing request headers:", request.headers)

            # return self._original_send(client, request, **kwargs)

        httpx.Client.send = instrumented_send

    def _uninstrument(self, **kwargs):
        if self._original_send:
            httpx.Client.send = self._original_send
            self._original_send = None

    def get_current_span(self) -> Optional[Span]:
        import langchain_core

        run_id: Optional[UUID] = None
        config = langchain_core.runnables.config.var_child_runnable_config.get()
        logger.warning(f"CONIFG --> {config}")
        if not isinstance(config, dict):
            return None
        for v in config.values():
            if not isinstance(v, langchain_core.callbacks.BaseCallbackManager):
                continue
            if run_id := v.parent_run_id:
                break
        if not run_id:
            return None
        return self._tracer.get_span(run_id)
