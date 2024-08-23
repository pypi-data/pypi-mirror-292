import asyncio
import os

class Runner:
    """Run external command with output capturing.
    Usage:
        runner = Runner(program, args, interval)
        runner.start()
        async for stdout, stderr in runner.stream():
            ...
        returncode = runner.wait()
    """

    def __init__(self, program, args, interval=1):
        self.proc = None
        self.program = program
        self.args = args
        self.interval = interval

    # async def start(self):
    #     cmd = self.program + " " + " ".join(self.args)
    #     self.proc = await asyncio.create_subprocess_shell(
    #         cmd,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #     )

    async def start(self):
        self.proc = await asyncio.create_subprocess_exec(
            self.program,
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # preexec_fn=os.setpgrp
        )

    async def stream(self):
        while True:
            if self.proc.stdout.at_eof() and self.proc.stderr.at_eof():
                break

            stdout = await self.proc.stdout.readline()
            stderr = await self.proc.stderr.readline()
            yield stdout.decode(), stderr.decode()

            await asyncio.sleep(self.interval)

    async def wait(self):
        if self.proc is None:
            return None

        await self.proc.communicate()
        return self.proc.returncode


