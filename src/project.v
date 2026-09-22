/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_8_bit_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire load_en   = ui_in[0];
  wire count_en  = ui_in[1];
  wire output_en = ui_in[2];

  reg [7:0] counter_reg;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      counter_reg <= 8'd0;
    end else begin
      if (load_en) begin
        counter_reg <= uio_in;            // Load takes highest priority
      end else if (count_en) begin
        counter_reg <= counter_reg + 1'b1; // Count only when count_en is high
      end
      // Implicit else: retain current value when count_en is low
    end
  end

  assign uio_oe  = output_en ? 8'hFF : 8'h00;
  assign uio_out = counter_reg;
  assign uo_out  = counter_reg;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[7:3], 1'b0};

endmodule