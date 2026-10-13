# Role Map

Generated: 2026-10-13T19:39:08Z

| Dataset | Role | Depends on | Dependents | Status |
|---|---|---|---|---|
| dat_01 | AT command reference | - | dat_02,03,04,06,09,10,11,12,13,15,17 | partial |
| dat_02 | URC reference | dat_01, dat_05 | - | partial |
| dat_03 | Error code reference | dat_01 | - | partial |
| dat_04 | Timing reference | dat_01, dat_05 | - | partial |
| dat_05 | State machine reference | dat_01 | dat_02,04,06 | partial |
| dat_06 | Init sequence reference | dat_01, dat_05 | - | partial |
| dat_07 | Hardware reference | - | dat_13, dat_16 | partial |
| dat_08 | Firmware compatibility | external | - | blocked |
| dat_09 | SMS reference | dat_01 | - | partial |
| dat_10 | GPRS reference | dat_01 | - | partial |
| dat_11 | HTTP/FTP/SSL reference | dat_01 | dat_17 | partial |
| dat_12 | Audio reference | dat_01 | - | partial |
| dat_13 | SIM management reference | dat_01, dat_07 | - | partial |
| dat_14 | Operator/APN reference | external | dat_10 | partial |
| dat_15 | Power reference | dat_01 | - | partial |
| dat_16 | Board/EVB reference | - | - | blocked |
| dat_17 | Cert/Key store reference | dat_01, dat_11 | - | partial |
| dat_18 | Certification | external | - | blocked |