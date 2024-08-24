import io
import os
import string
import textwrap
from typing import Optional

import aiohttp
from pydantic import validate_arguments

from rtex.constants import DEFAULT_API_HOST, FORMAT_MIME
from rtex.exceptions import RtexError, YouNeedToUseAContextManager
from rtex.models import (
    CreateLaTeXDocumentRequest,
    CreateLaTeXDocumentResponse,
    RenderDensity,
    RenderFormat,
    RenderQuality,
)


class AsyncRtexClient:
    def __init__(
        self,
        api_host=os.environ.get("RTEX_API_HOST", DEFAULT_API_HOST),
    ):
        self.api_host = api_host
        self.latex_template = string.Template(
            textwrap.dedent(
                r"""
                \documentclass{$docclass}
                \begin{document}
                $doc
                \end{document}
                """
            )
        )

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession(
            base_url=self.api_host,
            headers={
                "Content-Type": "application/json",
            },
        ).__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.session.__aexit__(exc_type, exc_val, exc_tb)

    def _oops_no_session(self):
        if not self.session:
            raise YouNeedToUseAContextManager(
                textwrap.dedent(
                    f"""\
                {self.__class__.__name__} keeps a aiohttp.ClientSession under
                the hood and needs to be closed when you're done with it. But
                since there isn't an async version of __del__ we have to use
                __aenter__/__aexit__ instead. Apologies.

                Instead of

                    myclient = {self.__class__.__name__}()
                    myclient.text_to_image(...)

                Do this

                    async with {self.__class__.__name__} as myclient:
                        myclient.text_to_image(...)

                Note that it's `async with` and not `with`.
                """
                )
            )

    @validate_arguments
    async def create_render(
        self,
        code: str,
        format: RenderFormat = "png",
        documentclass: str = "minimal",
        quality: Optional[RenderQuality] = None,
        density: Optional[RenderDensity] = None,
    ):
        self._oops_no_session()

        final_doc = self.latex_template.substitute(
            docclass=documentclass,
            doc=code,
        )

        request_body = CreateLaTeXDocumentRequest(
            code=final_doc,
            format=format,
            quality=quality,
            density=density,
        )

        res = await self.session.post(
            "/api/v2",
            headers={"Accept": "application/json"},
            data=request_body.json(
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
            ),
        )

        return CreateLaTeXDocumentResponse.parse_obj(await res.json()).__root__

    @validate_arguments(config={"arbitrary_types_allowed": True})
    async def save_render(
        self,
        filename: str,
        output_fd: io.IOBase,
        format: RenderFormat = "png",
    ):
        self._oops_no_session()

        res = await self.session.get(
            f"/api/v2/{filename}",
            headers={
                "Accept": FORMAT_MIME[format],
            },
        )

        async for chunk, _ in res.content.iter_chunks():
            output_fd.write(chunk)

    @validate_arguments
    async def get_render(
        self,
        filename: str,
        format: RenderFormat = "png",
    ):
        buf = io.BytesIO()
        await self.save_render(filename, buf, format)
        buf.seek(0)

        return buf

    @validate_arguments
    async def render_math(
        self,
        code: str,
        format: RenderFormat = "png",
        documentclass: str = "minimal",
        quality: Optional[RenderQuality] = None,
        density: Optional[RenderDensity] = None,
    ):
        final_doc = rf"\({code}\)"

        res = await self.create_render(
            code=final_doc,
            format=format,
            documentclass=documentclass,
            quality=quality,
            density=density,
        )

        if res.status == "error":
            raise RtexError("Unknown error rendering code.")

        return await self.get_render(
            filename=res.filename,
            format=format,
        )
