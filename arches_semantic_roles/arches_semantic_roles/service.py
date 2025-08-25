from time import sleep, time
import json
import uuid
from django.conf import settings
import logging
from threading import Event, Thread, Timer
from datetime import datetime, timedelta
from contextlib import contextmanager

from django.dispatch import receiver
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

_PROCESS_KEY = str(uuid.uuid4())
CASBIN_TRIGGER_DEBOUNCE_SECONDS = int(settings.CASBIN_TRIGGER_DEBOUNCE_SECONDS)
DEBOUNCE = timedelta(seconds=60)
MINIMUM_REFRESH_PERIOD: None | float = settings.CASBIN_TRIGGER_MINIMUM_REFRESH_SECONDS

class ArchesRBACPermissionService:
    last_run: datetime | None = None # TODO: or Timer is cleaner
    _update_sets: bool = False
    _update_casbin: bool = False
    initialized: bool = False

    def initialize(self):
        ...

    def reload(self):
        from arches.app.utils.permission_backend import _get_permission_framework
        casbin_framework = _get_permission_framework()
        casbin_framework.recalculate_table()
        casbin_framework._enforcer.load_policy()

    def listen(self):
        self.reload()

    def trip(self, update_sets=True, update_casbin=True):
        need_timer = False
        if update_sets and not self._update_sets:
            need_timer = True
            self._update_sets = True

        if update_casbin and not self._update_casbin:
            need_timer = True
            self._update_casbin = True

        if need_timer:
            self._timer = Timer(
                CASBIN_TRIGGER_DEBOUNCE_SECONDS,
                self.execute_recalculate_loop
            )
            self._timer.start()

    def do_request_reload(self):
        print("Nothing to do as single-process") # TODO
        #self.listen()

    def request_reload(self):
        this_run = datetime.now()
        self._update_casbin = False
        if self.last_run and self.last_run - this_run < DEBOUNCE:
            sleep(min((self.last_run - this_run).seconds, 0.001))

        self.do_request_reload()

        self.last_run = this_run

    def update_set_membership(self):
        # Cannot be loaded before DB is ready
        from arches_inclusion_rule.utils.es_set_applicator import SetApplicator

        self._update_sets = False
        set_applicator = SetApplicator(print_statistics=True, wait_for_completion=True)
        set_applicator.apply_sets()

    def execute_recalculate_loop(self):
        logger.info("Starting recalculate loop")
        if self._update_casbin:
            self._update_casbin = False
            self.listen()
        if self._update_sets:
            self._update_sets = False
            self.update_set_membership()


class CasbinInProcessTrigger(ArchesRBACPermissionService):
    ...

class CasbinTrigger(ArchesRBACPermissionService):
    wait_time = CASBIN_TRIGGER_DEBOUNCE_SECONDS
    _timer = None

    @staticmethod
    @contextmanager
    def connect():
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASS
        )
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            credentials=credentials,
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.CASBIN_RELOAD_QUEUE, exchange_type="fanout")
        channel.queue_declare(queue=_PROCESS_KEY, durable=False)
        channel.queue_bind(exchange=settings.CASBIN_RELOAD_QUEUE, queue=_PROCESS_KEY, routing_key=settings.CASBIN_RELOAD_QUEUE)
        channel.basic_qos(prefetch_count=1)
        try:
            yield channel
        finally:
            connection.close()

    def listen(self):
        print("Listening")
        # This requires a live DB before this import can be used

        self._timer

        def _reload_real():
            self._timer = None
            print("Policy loading")
            self.reload()
            print("Policy loaded")

        def _reload(channel, method, properties, body):
            try:
                if body:
                    body = json.loads(body)

                # Helps avoid unnecessary reloading in the producer.
                if not body or body.get("processKey", True) != str(_PROCESS_KEY):
                    if self._timer is not None:
                        print("CASBIN-TRIGGER: debounce")
                        self._timer.cancel()
                    else:
                        print("CASBIN-TRIGGER: setting up")
                    self._timer = Timer(
                        self.wait_time,
                        _reload_real
                    )
                    self._timer.start()
                    print("CASBIN-TRIGGER: resetting in", self.wait_time)
                else:
                    print("CASBIN-TRIGGER: ignoring reload request")

                channel.basic_ack(delivery_tag=method.delivery_tag)
            except:
                logger.exception("Casbin listener exception")

        print("Attempting connect")
        with self.connect() as channel:
            print("Consuming")
            channel.basic_consume(
                queue=_PROCESS_KEY,
                on_message_callback=_reload,
            )
            channel.start_consuming()
            print("Exiting Casbin listener")

    def do_request_reload(self):
        timestamp = time()
        with self.connect() as channel:
            channel.basic_publish(
                exchange=settings.CASBIN_RELOAD_QUEUE,
                routing_key=settings.CASBIN_RELOAD_QUEUE,
                body=json.dumps({"processKey": str(_PROCESS_KEY)}),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Transient,
                    timestamp=int(timestamp),
                    expiration="1000",
                )
            )

if settings.ENABLE_CASBIN_TRIGGER:
    try:
        import pika
    except ImportError:
        logger.error("Could not load Casbin because ENABLE_CASBIN_TRIGGER is set and pika is not available")
    trigger = CasbinTrigger()
else:
    trigger = CasbinInProcessTrigger()

# This is ugly, but no point in tidying until we can reach resource_indexed again
# UPDATE_SETS_FOR_RESOURCE_RUNNING = False
# UPDATE_SETS_FOR_RESOURCE_RUNNING_TO_RUN = set()
# @receiver(resource_indexed)
# def update_sets_for_resource(sender, instance, **kwargs):
#     from coral.utils.casbin import SetApplicator
#     # This may run too quickly
#     # Instead, it should trigger a (debounced) recalc.
#     # This may still require delays _between_ the upserts also.
#     def _exec():
#         global UPDATE_SETS_FOR_RESOURCE_RUNNING
#         global UPDATE_SETS_FOR_RESOURCE_RUNNING_TO_RUN
#         
#         set_applicator = SetApplicator(print_statistics=True, wait_for_completion=True)
#         UPDATE_SETS_FOR_RESOURCE_RUNNING_TO_RUN.add(instance.resourceinstanceid)
#         if UPDATE_SETS_FOR_RESOURCE_RUNNING:
#             return
#         UPDATE_SETS_FOR_RESOURCE_RUNNING = True
#         resources_to_run = set(UPDATE_SETS_FOR_RESOURCE_RUNNING_TO_RUN)
#         UPDATE_SETS_FOR_RESOURCE_RUNNING_TO_RUN = {}
#         try:
#             for resourceinstanceid in resources_to_run :
#                 set_applicator.apply_sets(resourceinstanceid=resourceinstanceid)
#         except Exception as exc:
#             print("Apply sets failed with", exc)
#             time.sleep(3.0)
#         finally:
#             UPDATE_SETS_FOR_RESOURCE_RUNNING = False
#     Timer(3.0, _exec).start()

# Not all saves trigger this (e.g. bulk) so a refresh period is still wise
# TODO: if I recall right, this can happen before the indexing is finished (unlike the signal above)
@receiver(post_save)
def update_casbin(sender, instance, **kwargs):
    from arches.app.models.resource import Resource
    casbin_relevant_graph_ids = {m["graphid"] for m in settings.WELL_KNOWN_RESOURCE_MODELS if m["model_name"] in ("Person", "Group", "Set", "Logical Set")}
    if isinstance(instance, Resource):
        recalculate_casbin = str(instance.graph_id) in casbin_relevant_graph_ids
        trigger.trip(update_casbin=recalculate_casbin, update_sets=True)
