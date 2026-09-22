# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set clock to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # 1. Verify reset state
    dut._log.info("Verify reset state")
    assert dut.uo_out.value == 0, f"Expected 0 after reset, got {dut.uo_out.value}"

    # 2. Test pause/hold when count_en = 0
    dut._log.info("Test counter hold when count_en is 0")
    dut.ui_in.value = 0b000  # count_en = 0, load_en = 0
    await ClockCycles(dut.clk, 2)
    assert dut.uo_out.value == 0, f"Expected counter to stay 0, got {dut.uo_out.value}"

    # 3. Test counting with count_en = 1 (ui_in[1] = 1)
    dut._log.info("Test counting with count_en enabled")
    dut.ui_in.value = 0b010  # count_en = 1, load_en = 0
    for expected in range(1, 5):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == expected, f"Expected {expected}, got {dut.uo_out.value}"

    # 4. Test parallel load (ui_in[0] = 1)
    dut._log.info("Test parallel load")
    dut.uio_in.value = 0xFE  # Load 254
    dut.ui_in.value = 0b001  # load_en = 1
    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0xFE, f"Expected 0xFE, got {dut.uo_out.value}"

    # 5. Test rollover (0xFE -> 0xFF -> 0x00 -> 0x01)
    dut._log.info("Test rollover behavior")
    dut.ui_in.value = 0b010  # load_en = 0, count_en = 1

    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0xFF, f"Expected 0xFF, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0x00, f"Expected 0x00, got {dut.uo_out.value}"

    await ClockCycles(dut.clk, 1)
    assert dut.uo_out.value == 0x01, f"Expected 0x01, got {dut.uo_out.value}"

    # 6. Test output enable (ui_in[2] = 1)
    dut._log.info("Test bidirectional output enable")
    dut.ui_in.value = 0b100  # output_en = 1
    await ClockCycles(dut.clk, 1)
    assert dut.uio_oe.value == 0xFF, f"Expected uio_oe to be 0xFF, got {dut.uio_oe.value}"

    dut.ui_in.value = 0b000  # output_en = 0
    await ClockCycles(dut.clk, 1)
    assert dut.uio_oe.value == 0x00, f"Expected uio_oe to be 0x00, got {dut.uio_oe.value}"

    dut._log.info("All tests passed successfully!")