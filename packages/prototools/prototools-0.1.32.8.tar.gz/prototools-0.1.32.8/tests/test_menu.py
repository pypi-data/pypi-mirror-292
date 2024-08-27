import os
import time
from threading import Thread
from unittest import main, TestCase
from unittest.mock import Mock, patch

import prototools.components as c
import prototools.menu as m


class ThreadedReturnGetter(Thread):

    def __init__(self, function, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        self.returned_value = None
        self.function = function
        try:
            super(ThreadedReturnGetter, self).__init__(
                target=self.get_return_value, args=args, kwargs=kwargs, daemon=True
            )
        except TypeError:
            super(ThreadedReturnGetter, self).__init__(
                target=self.get_return_value, args=args, kwargs=kwargs
            )
            self.daemon = True

    def get_return_value(self, *args, **kwargs):
        self.return_value = self.function(*args, **kwargs)


class BaseTestCase(TestCase):

    def setUp(self):
        self.mock_screen = Mock(spec=c.Screen())
        self.mock_screen.input.return_value = 4

        self.patcher = patch(target='prototools.menu.Screen', new=self.mock_screen)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)


class TestSampleMenu(BaseTestCase):
    
    def setUp(self):
        super(TestSampleMenu, self).setUp()
        self.menu = m.Menu("self.menu", "TestSample")
        self.item1 = m.Item("self.item1", self.menu)
        self.item2 = m.Item("self.item2", self.menu)
        self.menu.add_item(self.item1)
        self.menu.add_item(self.item2)
        self.menu.start()
        self.menu.wait_for_start(timeout=10)

    def tearDown(self) -> None:
        super(TestSampleMenu, self).tearDown()
        self.menu.exit()
        self.menu.join(timeout=10)

    def test_menu_init(self):
        self.assertIsInstance(self.menu, m.Menu)

    def test_exit(self):
        self.assertTrue(self.menu.is_alive())
        self.menu.exit()
        self.menu.join(timeout=10)
        self.assertFalse(self.menu.is_alive())


class TestMenu(BaseTestCase):

    def setUp(self):
        super(TestMenu, self).setUp()
        m.Menu.currently_active_menu = None

    def test_init(self):
        menu1 = m.Menu()
        menu2 = m.Menu("menu2", "test_init", show_exit_option=True)
        menu3 = m.Menu(title="menu3", subtitle="test_init", show_exit_option=False)
        self.assertEqual(menu1.title, "Menu")
        self.assertEqual(menu2.title, "menu2")
        self.assertEqual(menu3.title, "menu3")
        self.assertIsNone(menu1.subtitle)
        self.assertEqual(menu2.subtitle, "test_init")
        self.assertEqual(menu3.subtitle, "test_init")
        self.assertTrue(menu1.show_exit_option)
        self.assertTrue(menu2.show_exit_option)
        self.assertFalse(menu3.show_exit_option)

    def test_currently_active_menu(self):
        menu1 = m.Menu("menu1", "test_currently_active_menu_1")
        menu2 = m.Menu("menu2", "test_currently_active_menu_2")
        menu3 = m.Menu("menu3", "test_currently_active_menu_3")
        self.assertIsNone(m.Menu.currently_active_menu)
        menu1.start()
        menu1.wait_for_start(timeout=10)
        self.assertIs(m.Menu.currently_active_menu, menu1)
        menu2.start()
        menu2.wait_for_start(timeout=10)
        self.assertIs(m.Menu.currently_active_menu, menu2)
        menu3.start()
        menu3.wait_for_start(timeout=10)
        self.assertIs(m.Menu.currently_active_menu, menu3)

    def test_remove_menu_item(self):
        menu = m.Menu("menu", "test_remove_menu_item")
        item1 = m.Item("item1", menu=menu)
        item2 = m.Item("item2", menu=menu)
        menu.add_item(item1)
        menu.add_item(item2)
        self.assertIn(item1, menu.items)
        self.assertIn(item2, menu.items)
        menu.remove_item(item1)
        self.assertNotIn(item1, menu.items)
        self.assertIn(item2, menu.items)


if __name__ == '__main__':
    main()