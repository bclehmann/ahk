import asyncio
import subprocess
import time
import sys
import os
from unittest import IsolatedAsyncioTestCase


project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk.daemon import AHKDaemon
from ahk.window import AsyncWindow


class TestMouseAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AHKDaemon()
        await self.ahk.start()

    def tearDown(self) -> None:
        self.ahk.stop()

    async def test_mouse_move(self):
        x, y = await self.ahk.mouse_position
        await self.ahk.mouse_move(10, 10, relative=True)
        assert await self.ahk.mouse_position == (x+10, y+10)


class TestWindowAsync(IsolatedAsyncioTestCase):
    win: AsyncWindow
    async def asyncSetUp(self):
        self.ahk = AHKDaemon()
        await self.ahk.start()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    async def test_transparent(self):
        self.assertEqual(await self.win.get_transparency(), 255)

        await self.win.set_transparency(220)
        self.assertEqual(await self.win.get_transparency(), 220)

        self.win.transparent = 255
        await asyncio.sleep(0.5)
        self.assertEqual(await self.win.transparent, 255)


    async def test_pinned(self):
        self.assertFalse(await self.win.always_on_top)

        await self.win.set_always_on_top(True)
        self.assertTrue(await self.win.is_always_on_top())

        self.win.always_on_top = False
        await asyncio.sleep(1)
        self.assertFalse(await self.win.always_on_top)

    async def test_close(self):
        await self.win.close()
        await asyncio.sleep(0.2)
        self.assertFalse(await self.win.exists())
        self.assertFalse(await self.win.exist)

    async def test_show_hide(self):
        await self.win.hide()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

        await self.win.show()
        await asyncio.sleep(0.5)
        self.assertTrue(await self.win.exist)

    async def test_kill(self):
        await self.win.kill()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

    async def test_max_min(self):
        self.assertTrue(await self.win.non_max_non_min)
        self.assertFalse(await self.win.is_minmax())

        await self.win.maximize()
        await asyncio.sleep(1)
        self.assertTrue(await self.win.maximized)
        self.assertTrue(await self.win.is_maximized())

        await self.win.minimize()
        await asyncio.sleep(1)
        self.assertTrue(await self.win.minimized)
        self.assertTrue(await self.win.is_minimized())

        await self.win.restore()
        await asyncio.sleep(0.5)
        self.assertTrue(await self.win.maximized)
        self.assertTrue(await self.win.is_maximized())
#
    async def test_names(self):
        self.assertEqual(await self.win.class_name, b'Notepad')
        self.assertEqual(await self.win.get_class_name(), b'Notepad')

        self.assertEqual(await self.win.title, b'Untitled - Notepad')
        self.assertEqual(await self.win.get_title(), b'Untitled - Notepad')

        self.assertEqual(await self.win.text, b'')
        self.assertEqual(await self.win.get_text(), b'')

    async def test_title_setter(self):
        starting_title = await self.win.title
        await self.win.set_title("new title")
        assert await self.win.get_title() != starting_title

    async def asyncTearDown(self):
        self.ahk.stop()
        self.p.terminate()
        await asyncio.sleep(0.5)
