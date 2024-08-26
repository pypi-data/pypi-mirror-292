# coding: utf-8

import unittest
import time
import os
import importlib.util
from json import loads
from tinymoss.nodes import MossNode
import sys
import logging
from tinymoss import TinyMoss

# LOGGER_FMT = ''


class TinyMossTest(unittest.TestCase):

    def test_tinymoss(self):
        #logging.basicConfig(level=logging.DEBUG)

        downcount = 3

        print()
        print('*' * 80)
        print('TMoss 测试程序 {} 秒后自动结束'.format(downcount))
        print('*' * 80)

        moss = TinyMoss()
        
        moss.startup()
        
        self.assertTrue(len(moss.all_nodes()) == 2)
        
        _node = moss.find_node('urn:sensor:id:5cf3ed19-571d-4631-9bb0-e62de70bedea')
        self.assertTrue(_node is not None)


        try:
            while downcount > 0:
                time.sleep(1)
                downcount -= 1
        except KeyboardInterrupt:
            self.assertTrue(True)
            moss.shutdown()
        except:
            self.assertTrue(False)


if __name__ == '__main__':

    unittest.main(verbosity=2)
