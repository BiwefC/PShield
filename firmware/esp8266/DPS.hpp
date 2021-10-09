#pragma once

#include <Arduino.h>

#define ADDR_MCU              0x5f
#define ADDR_EEPROM           0x57

#define REGS_FLAGS            0x2
#define REGS_U_IN             0x8    // scale 32.0
#define REGS_I_IN             0xa    // scale 128.0
#define REGS_P_IN             0xc    // scale 2.0
#define REGS_U_OUT            0xe    // scale 254.5
#define REGS_I_OUT            0x10   // scale 128.0
#define REGS_P_OUT            0x12   // scale 2.0
#define REGS_T_INTAKE         0x1a   // scale 32.0
#define REGS_T_INTERNAL       0x1c   // scale 32.0
#define REGS_FAN_SPEED        0x1e   // scale 1.0

#define REGS_ON_SECONDS       0x30   // scale 2.0
#define REGS_MAX_P_IN         0x32   // scale 2.0
#define REGS_MIN_I_IN         0x34   // scale 128.0
#define REGS_MAX_I_OUT        0x36   // scale 128.0
#define REGS_FAN_RPM_TARGET   0x40   // scale 1.0

byte calculate_check_sum(byte reg, byte data0, byte data1);
word read_dsp_mcu(byte reg);
void write_dsp_mcu(byte reg, word value);