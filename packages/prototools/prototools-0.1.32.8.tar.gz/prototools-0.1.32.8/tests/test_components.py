import os
import time
from unittest import main, TestCase
from unittest.mock import patch

import prototools.components as c
import prototools.menu as m


def print_screen_edge(width=80):
    msg = '{title:{fill}^{width}}'.format(
        title='simulate screen edges', fill='-', width=(width - 2)
    )
    print('{edge}{msg}{edge}'.format(edge="|", msg=msg))


class TestScreen(TestCase):

    def test_clear(self):
        screen = c.Screen()
        screen.println("Clearing screen...")
        screen.clear()

    @patch('prototools.components.Screen.input', return_value='Done')
    def test_input(self, mock_input):
        screen = c.Screen()
        input_string = screen.input(prompt="A message")
        self.assertEqual(input_string, 'Done')

    def test_flush(self):
        screen = c.Screen()
        screen.println("Print all at once...")
        for _ in range(40):
            screen.printf("\\")
        screen.println()
        screen.println("Next line")
        for _ in range(40):
            screen.printf("/")
            screen.flush()
        screen.println()

    def test_printf(self):
        screen = c.Screen()
        screen.printf("Printing...")
        screen.printf("Line 1", "Line 2 \n", "Line 3")
        screen.printf("A %s message" % "printf-style")
        screen.printf("This is a {} message".format("format-style"))

    def test_println(self):
        screen = c.Screen()
        screen.println("Printing...")
        screen.println("Line 1", "Line 2 \n", "Line 3\n")
        screen.println("A %s message" % "printf-style")
        screen.println("This is a {} message".format("format-style"))

    def test_screen_size(self):
        screen = c.Screen()
        screen.println("Screen height: %s" % screen.height)
        screen.println("Screen width: %s" % screen.width)
        self.assertEqual(screen.height, 40)
        self.assertEqual(screen.width, 80)


class TestStyle(TestCase):

    def test_margin(self):
        m = c.Margin()
        self.assertEqual(m.top, 1)
        self.assertEqual(m.bottom, 0)
        self.assertEqual(m.left, 2)
        self.assertEqual(m.right, 2)

    def test_padding(self):
        p = c.Padding()
        self.assertEqual(p.top, 1)
        self.assertEqual(p.bottom, 1)
        self.assertEqual(p.left, 2)
        self.assertEqual(p.right, 2)
    
    def test_border_type_ascii(self):
        b = c.Border("ascii")
        self.assertEqual(b.top_left, '+')
        self.assertEqual(b.top_right, '+')
        self.assertEqual(b.bottom_left, '+')
        self.assertEqual(b.bottom_right, '+')
        self.assertEqual(b.vertical, '|')
        self.assertEqual(b.vertical_left, '+')
        self.assertEqual(b.vertical_right, '+')
        self.assertEqual(b.horizontal, '-')
        self.assertEqual(b.horizontal_top, '+')
        self.assertEqual(b.horizontal_bottom, '+')
        self.assertEqual(b.intersection, '+')

    def test_border_type_light(self):
        b = c.Border("light")
        self.assertEqual(b.top_left, u"\u250C")
        self.assertEqual(b.top_right, u"\u2510")
        self.assertEqual(b.bottom_left, u"\u2514")
        self.assertEqual(b.bottom_right, u"\u2518")
        self.assertEqual(b.vertical, u"\u2502")
        self.assertEqual(b.vertical_left, u"\u251C")
        self.assertEqual(b.vertical_right, u"\u2524")
        self.assertEqual(b.horizontal, u"\u2500")
        self.assertEqual(b.horizontal_top, u"\u252C")
        self.assertEqual(b.horizontal_bottom, u"\u2534")
        self.assertEqual(b.intersection, u"\u253C")

    def test_border_type_double(self):
        b = c.Border("double")
        self.assertEqual(b.top_left, u"\u2554")
        self.assertEqual(b.top_right, u"\u2557")
        self.assertEqual(b.bottom_left, u"\u255A")
        self.assertEqual(b.bottom_right, u"\u255D")
        self.assertEqual(b.vertical, u"\u2551")
        self.assertEqual(b.vertical_left, u"\u2560")
        self.assertEqual(b.vertical_right, u"\u2563")
        self.assertEqual(b.horizontal, u"\u2550")
        self.assertEqual(b.horizontal_top, u"\u2566")
        self.assertEqual(b.horizontal_bottom, u"\u2569")
        self.assertEqual(b.intersection, u"\u256C")

    def test_border_type_heavy(self):
        b = c.Border("heavy")
        self.assertEqual(b.top_left, u"\u250F")
        self.assertEqual(b.top_right, u"\u2513")
        self.assertEqual(b.bottom_left, u"\u2517")
        self.assertEqual(b.bottom_right, u"\u251B")
        self.assertEqual(b.vertical, u"\u2503")
        self.assertEqual(b.vertical_left, u"\u2523")
        self.assertEqual(b.vertical_right, u"\u252B")
        self.assertEqual(b.horizontal, u"\u2501")
        self.assertEqual(b.horizontal_top, u"\u2533")
        self.assertEqual(b.horizontal_bottom, u"\u253B")
        self.assertEqual(b.intersection, u"\u254B")

    def test_style(self):
        s = c.Style()
        self.assertEqual(s.margin.top, c.Margin().top)
        self.assertEqual(s.padding.bottom, c.Padding().bottom)
        self.assertEqual(s.border.top_left, c.Border("light").top_left)


class TestDimension(TestCase):

    def test_dimension(self):
        d = c.Dimension()
        self.assertEqual(d.width, 0)
        self.assertEqual(d.height, 0)
        d.width = 80
        d.height = 40
        self.assertEqual(d.width, 80)
        self.assertEqual(d.height, 40)
        self.assertEqual(str(d), "80x40")


class TestComponent(TestCase):

    def test_component(self):
        cc = c.Component()
        self.assertEqual(cc.style.margin.top, 1)
        self.assertEqual(cc.style.margin.bottom, 0)
        self.assertEqual(cc.style.margin.left, 2)
        self.assertEqual(cc.style.margin.right, 2)
        self.assertEqual(cc.style.padding.top, 1)
        self.assertEqual(cc.style.padding.bottom, 1)
        self.assertEqual(cc.style.padding.left, 2)
        self.assertEqual(cc.style.padding.right, 2)
        self.assertEqual(cc.style.border.vertical, u"\u2502")
        self.assertEqual(cc.max_dimension.width, 80)
        self.assertEqual(cc.max_dimension.height, 40)

    def test_component_calculations(self):
        cc = c.Component()
        cc.style.margin.left = 1
        cc.style.margin.right = 1
        cc.style.padding.left = 2
        cc.style.padding.right = 2
        self.assertEqual(cc._calculate_border_width(), 77)
        self.assertEqual(cc._calculate_content_width(), 71)

    def test_box(self):
        print_screen_edge()
        t = "Prototools"
        s = "... faster development"
        b = c.Box(title=t, subtitle=s, subtitle_align="right")
        for line in b.generate():
            print(line)
        c.render(b)

    def test_header(self):
        print_screen_edge()
        h = c.Header(title="Prototools")
        for line in h.generate():
            print(line)
        c.render(h)

    def test_text(self):
        print_screen_edge()
        t = c.Text(text="This is a text section")
        for line in t.generate():
            print(line)
        c.render(t)
    
    def test_items(self):
        print_screen_edge()
        options = [m.Item(text="Option 1"), m.Item(text="Option 2")]
        items = c.Items(items=options)
        for line in items.generate():
            print(line)
        c.render(items)

    def test_footer(self):
        print_screen_edge()
        f = c.Footer()
        for line in f.generate():
            print(line)
        c.render(f)

    def test_prompt(self):
        print_screen_edge()
        p = c.Prompt(prompt=">>> Enter a value")
        for line in p.generate():
            print(line)
        c.render(p)
        print_screen_edge()


if __name__ == '__main__':
    main()