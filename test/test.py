# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset sequence
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # 1. Verify reset values
    dut._log.info("Verify reset state")
    assert dut.uo_out.value == 0, f"Expected 0 after reset, got {dut.uo_out.value}"
    assert dut.uio_out.value == 0, f"Expected uio_out to be 0, got {dut.uio_out.value}"
    assert dut.uio_oe.value == 0x00, f"Expected uio_oe to be 0x00, got {dut.uio_oe.value}"

    # 2. Test free-running counting (with load_en = 0)
    dut._log.info("Test counting")
    for expected in range(1, 5):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == expected, f"Expected {expected}, got {dut.uo_out.value}"
        assert dut.uio_out.value == expected

    # 3. Test parallel load via uio_in (load_en is ui_in[0])
    dut._log.info("Test synchronous load")
    dut.uio_in.value = 0xFE  # Load 254 (close to rollover)
    dut.ui_in.value = 0b001  # load_en = 1
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0xFE, f"Expected loaded value 0xFE, got {dut.uo_out.value}"

    # 4. Test rollover (0xFE -> 0xFF -> 0x00 -> 0x01)
    dut._log.info("Test rollover behavior")
    dut.ui_in.value = 0b000  # Disable load_en to resume counting

    # Next cycle -> 0xFF
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0xFF, f"Expected 0xFF, got {dut.uo_out.value}"

    # Rollover cycle -> 0x00
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0x00, f"Expected 0x00 after rollover, got {dut.uo_out.value}"

    # Next cycle -> 0x01
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0x01, f"Expected 0x01, got {dut.uo_out.value}"

    # 5. Test output enable on bidirectional pins (output_en is ui_in[2])
    dut._log.info("Test bidirectional output enable (uio_oe)")
    dut.ui_in.value = 0b100  # output_en = 1
    await ClockCycles(dut.clk, 1)
    assert dut.uio_oe.value == 0xFF, f"Expected uio_oe to be 0xFF, got {dut.uio_oe.value}"

    dut.ui_in.value = 0b000  # output_en = 0
    await ClockCycles(dut.clk, 1)
    assert dut.uio_oe.value == 0x00, f"Expected uio_oe to be 0x00, got {dut.uio_oe.value}"

    dut._log.info("All tests completed successfully!")