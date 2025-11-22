#include "cc1100_raspi.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

// Simple demo to select a CC1101 profile and dump register configuration after applying.
// Usage: ./rx_profile_demo -mTPMS | -mIoT | -mOOK | -mGFSK100
// Additional options:
//   -addr <dec>      Set node address (default 1)
//   -freq <1|2|3|4>  ISM band: 1=315,2=433,3=868,4=915 (profile overrides may retune)
//   -channel <n>     Channel number (default 0)
// Profiles added:
//   TPMS (mode 0x07) and IoT (mode 0x08)

static void usage() {
    printf("CC1101 RX Profile Demo\n");
    printf("Usage: rx_profile_demo [-mTPMS|-mIoT|-mGFSK100|-mOOK] [options]\n");
    printf("Options:\n");
    printf("  -addr <dec>       Node address (default 1)\n");
    printf("  -freq <1|2|3|4>   ISM band select (default 3=868)\n");
    printf("  -channel <n>      Channel (default 0)\n");
    printf("  -h                Help\n");
}

int main(int argc, char *argv[]) {
    uint8_t addr = 1;
    int mode = 0x03;          // default GFSK_100_kb
    int freq = 0x03;          // default 868.3 MHz
    int channel = 0;          // default channel

    for(int i=1;i<argc;i++) {
        if(strcmp(argv[i],"-h")==0) { usage(); return 0; }
        else if(strcmp(argv[i],"-mTPMS")==0) { mode = 0x07; freq = 0x02; } // TPMS uses 433.92 MHz
        else if(strcmp(argv[i],"-mIoT")==0) { mode = 0x08; freq = 0x03; }  // IoT IT+ at 868.3 MHz
        else if(strcmp(argv[i],"-mGFSK100")==0) { mode = 0x03; }
        else if(strcmp(argv[i],"-mOOK")==0) { mode = 0x06; }
        else if(strcmp(argv[i],"-addr")==0 && i+1<argc) { addr = (uint8_t)atoi(argv[++i]); }
        else if(strcmp(argv[i],"-freq")==0 && i+1<argc) { freq = atoi(argv[++i]); }
        else if(strcmp(argv[i],"-channel")==0 && i+1<argc) { channel = atoi(argv[++i]); }
        else {
            printf("Unknown argument: %s\n", argv[i]);
            usage();
            return 1;
        }
    }

    CC1100 radio;
    radio.set_debug_level(1);

    volatile uint8_t my_addr = addr;
    extern int cc1100_freq_select; cc1100_freq_select = freq;
    extern int cc1100_mode_select; cc1100_mode_select = mode;
    extern int cc1100_channel_select; cc1100_channel_select = channel;

    if(radio.begin(my_addr) == FALSE) {
        printf("Failed to init CC1101 (check wiring/SPI).\n");
        return 2;
    }

    printf("Applied profile mode=0x%02X freq_sel=%d channel=%d addr=%d\n", mode, freq, channel, addr);
    radio.show_register_settings();
    radio.end();
    return 0;
}
