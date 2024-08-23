from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
from kbraincortex.common.configuration import AZURE_SERVICE_BUS_CONNECTION_STRING

def publish_message(
        message: str, 
        topic_name: str, 
        application_properties: dict | None = None,
        connection_str: str = AZURE_SERVICE_BUS_CONNECTION_STRING
):
    properties_to_use = {"event_type": topic_name}
    if application_properties:
        properties_to_use.update(application_properties)

    servicebus_client = ServiceBusClient.from_connection_string(conn_str=connection_str)
    sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    message_object = ServiceBusMessage(message)
    message_object.application_properties = properties_to_use
    sender.send_messages(message_object)
    sender.close()
    servicebus_client.close()

def create_topic(topic_name: str, connection_str: str = AZURE_SERVICE_BUS_CONNECTION_STRING):
    admin_client = ServiceBusAdministrationClient.from_connection_string(conn_str=connection_str)
    admin_client.create_topic(topic_name)

def create_queue(queue_name: str, connection_str: str = AZURE_SERVICE_BUS_CONNECTION_STRING):
    admin_client = ServiceBusAdministrationClient.from_connection_string(conn_str=connection_str)
    admin_client.create_queue(queue_name)

def create_subscription(
        topic_name: str, 
        subscription_name: str,         
        connection_str: str = AZURE_SERVICE_BUS_CONNECTION_STRING
):
    admin_client = ServiceBusAdministrationClient.from_connection_string(conn_str=connection_str)
    admin_client.create_subscription(        
        topic_name, 
        subscription_name
    )
    
