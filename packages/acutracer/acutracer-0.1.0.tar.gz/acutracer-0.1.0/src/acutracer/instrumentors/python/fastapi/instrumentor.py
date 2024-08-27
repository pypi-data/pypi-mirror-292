import asyncio
from contextlib import asynccontextmanager, contextmanager
from functools import wraps

import httpx
import requests
from loguru import logger
from openinference.semconv.resource import ResourceAttributes
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from fastapi import FastAPI, Request
from src.acutracer.exporters.jaeger_exporter import CustomJaegerExporter


class FastAPIAppInstrumentor:
    def __init__(self, name="acutracer"):
        self.tracer_provider = trace_sdk.TracerProvider(
            resource=Resource.create({"service.name": name}),
            span_limits=trace_sdk.SpanLimits(max_attributes=10_000),
        )
        jeager_exporter = CustomJaegerExporter()
        self.tracer_provider.add_span_processor(jeager_exporter.get_processor())

        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)

    def instrument(self, app: FastAPI):
        FastAPIInstrumentor.instrument_app(app)

        @app.middleware("http")
        async def add_parent_trace(request: Request, call_next):
            logger.info(f"\n In add_parent_trace for request {request}, tracer: {self.tracer}")
            with self.tracer.start_as_current_span(f"APP http_request {request.method} {request.url}") as span:
                context = TraceContextTextMapPropagator().extract(request.headers)
                trace.set_span_in_context(span, context)

                # Add custom headers to the request state
                request.state.custom_headers = {
                    "X-cust-trace-id": f"{span.get_span_context().trace_id:032x}",
                    "X-cust-span-id": f"{span.get_span_context().span_id:016x}"
                }

                response = await call_next(request)
                return response

        def instrument_requests():
            original_send = requests.Session.send

            @wraps(original_send)
            def instrumented_send(session, request, **kwargs):
                with self.tracer.start_as_current_span(f"Requests {request.method} {request.url}") as span:
                    headers = request.headers
                    headers.update({
                        "X-cust-trace-id": f"{span.get_span_context().trace_id:032x}",
                        "X-cust-span-id": f"{span.get_span_context().span_id:016x}"
                    })
                    response = original_send(session, request, **kwargs)
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response_content_length", len(response.content))
                    return response

            requests.Session.send = instrumented_send

        def instrument_httpx():
            original_send = httpx.Client.send
            original_async_send = httpx.AsyncClient.send

            @wraps(original_send)
            def instrumented_send(client, request, **kwargs):
                try:
                    logger.info(f"\n in sync httpx send {self.tracer}")
                except Exception as e:
                    logger.error(f"ERROR {e}")
                with self.tracer.start_as_current_span(f"HTTP {request.method} {request.url}") as span:
                    headers = request.headers
                    headers.update({
                        "X-cust-trace-id": f"{span.get_span_context().trace_id:032x}",
                        "X-cust-span-id": f"{span.get_span_context().span_id:016x}"
                    })
                    logger.info(f"Updated Headers {headers}")
                    response = original_send(client, request, **kwargs)
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response_content_length", len(response.content))

                    return response

            @wraps(original_async_send)
            async def instrumented_async_send(self, request, **kwargs):
                logger.info("\n in A-sync httpx send")
                with self.tracer.start_as_current_span(f"HTTP {request.method} {request.url}") as span:
                    headers = request.headers
                    headers.update({
                        "X-cust-trace-id": f"{span.get_span_context().trace_id:032x}",
                        "X-cust-span-id": f"{span.get_span_context().span_id:016x}"
                    })
                    response = await original_async_send(self, request, **kwargs)
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response_content_length", len(response.content))
                    return response

            httpx.Client.send = instrumented_send
            httpx.AsyncClient.send = instrumented_async_send

        instrument_httpx()
        instrument_requests()

        return self.tracer
