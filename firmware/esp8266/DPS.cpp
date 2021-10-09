#include <Wire.h>
#include "DPS.hpp"


byte calculate_check_sum(byte reg, byte data0, byte data1)
{
    byte cs = (ADDR_MCU << 1) + reg + data0 + data1;
    byte reg_cs = (0xff - cs) + 1;

    return reg_cs;
}


word read_dsp_mcu(byte reg)
{
    byte cs = calculate_check_sum(reg, 0, 0);
    byte write_trans[2] = {reg, cs};

    Wire.beginTransmission(ADDR_MCU);
    Wire.write(write_trans, 3);
    if (Wire.endTransmission() != 0) {
        Serial.println("Write to DSP MCU Addr Error");
    }

    Wire.requestFrom(ADDR_MCU, 3);

    byte receive[3] = {0};

    receive[0] = Wire.read();
    receive[1] = Wire.read();
    receive[2] = Wire.read();

    word receive_word = word(receive[0]) | word(receive[1]) << 8;

    return receive_word;
}

void write_dsp_mcu(byte reg, word value)
{
    byte data_lsb = lowByte(value);
    byte data_msb = highByte(value);
    byte cs = calculate_check_sum(reg, data_msb, data_lsb);

    byte write_trans[4] = {reg, data_lsb, data_msb, cs};

    Wire.beginTransmission(ADDR_MCU);
    Wire.write(write_trans, 4);
    if (Wire.endTransmission() != 0) {
        Serial.println("Write to DSP MCU Error!");
    }

}