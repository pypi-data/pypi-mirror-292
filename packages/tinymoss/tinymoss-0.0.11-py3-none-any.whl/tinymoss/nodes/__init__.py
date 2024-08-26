# coding : utf-8

import threading
import functools
import logging
import time
import pika
from tinymoss.rabbits import RabbitMQConnection
from pika.exchange_type import ExchangeType
from abc import ABC, abstractmethod
import uuid

LOGGER = logging.getLogger(__name__)

class MossNode(threading.Thread, ABC):
  """TinyMoss节点， 提供节点之间的通信。 MossNode是线程安全的
  """
  
  def __init__(self, **kwargs):
    """初始化TinyMoss节点。 MossNode是线程安全的
    
      args:
        kwargs: amqp ,node_id, services, config, node_data
    """
    super(MossNode, self).__init__()
    self._reconnect_delay = 0
    self._amqp_url = kwargs['amqp'] if 'amqp' in kwargs else 'amqp://guest:guest@localhost:5672/%2F'
    self._connection = RabbitMQConnection(self._amqp_url)
    self.daemon =  True
    
    self.nodeId = kwargs['node_id'] if 'node_id' in kwargs else str(uuid.uuid4())
    self.services = kwargs['services'] if 'services' in kwargs else []
    self.config = kwargs['config'] if 'config' in kwargs else {}
    self.nodeData = kwargs['node_data'] if 'node_data' in kwargs else {}
    
    self._sub_queue()
    self._connection.add_on_message_callback(cb=self._on_messaged)


  def __repr__(self) -> str:
     return f'<MossNode ({self.nodeId})>'
  
  
  def _sub_queue(self):
    self._connection.sub_queue(self.nodeId, auto_delete=True)
    list(map(lambda service: self._connection.sub_queue(service, auto_delete=True), self.services))
  
  
  def _on_running(self):
    
    while not self._connection.was_consuming:
      time.sleep(.1)
    self.on_running()
  
  @abstractmethod
  def on_running(self):
    raise NotImplementedError()
  
  
  @abstractmethod
  def on_messaged(self, route, payload):
    pass
  
  
  def _on_messaged(self, route, payload):
    
    self.on_messaged(route, payload)
  
  
  def pub_to_node(self, node_id:str, payload:str | bytes):
    
    if self._connection.check_queue(node_id):
      self._connection.pub_queue(node_id, payload)
    else:
      LOGGER.debug('Trying to send a message to a queue that doesn\'t exist')
  
  
  def pub_to_service(self, service:str, payload:str|bytes):
    
    if self._connection.check_queue(service):
      self._connection.pub_queue(service, payload)
  
  
  def run(self):
      
      threading.Thread(target=self._on_running, daemon=True).start()
      while True:
          try:
              self._connection.run()
          except KeyboardInterrupt:
              self._connection.stop()
              break
          self._maybe_reconnect()

  def _maybe_reconnect(self):
      if self._connection.should_reconnect:
          self._connection.stop()
          reconnect_delay = self._get_reconnect_delay()
          LOGGER.info('Reconnecting after %d seconds', reconnect_delay)
          time.sleep(reconnect_delay)
          self._connection = RabbitMQConnection(self._amqp_url)
          self._sub_queue()
          

  def _get_reconnect_delay(self):
      if self._connection.was_consuming:
          self._reconnect_delay = 0
      else:
          self._reconnect_delay += 1
      if self._reconnect_delay > 30:
          self._reconnect_delay = 30
      return self._reconnect_delay

  
  