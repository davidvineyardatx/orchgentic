import pytest
from orchgentic.tools.core.datetime_now import DateTimeNowTool
from orchgentic.tools.core.filesystem_write import FileSystemWriteTool
from orchgentic.tools.core.filesystem_read import FileSystemReadTool

@pytest.mark.asyncio
async def test_datetime_tool():
    result = await DateTimeNowTool().execute()
    assert result.success is True
    assert result.tool_name == "datetime.now"

@pytest.mark.asyncio
async def test_filesystem_write_read(tmp_path):
    path = tmp_path / "hello.txt"
    write_result = await FileSystemWriteTool().execute(str(path), "hello")
    assert write_result.success is True
    read_result = await FileSystemReadTool().execute(str(path))
    assert read_result.success is True
    assert read_result.data == "hello"
