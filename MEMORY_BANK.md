# ASCEND PROJECT MEMORY BANK

## Successful Configurations
- **Date:** 2026-03-27 | **Action:** LiDAR-Only Trust Hack | **Status:** SUCCESS
- **Parameters:** `VISO_POS_M_NSE = 0.1`, `VISO_VEL_M_NSE = 0.1`, `VISO_YAW_M_NSE = 0.05`.

## Known Failures & Bugs
- **Date:** 2026-03-27 | **Action:** Tightening `PSC_POSXY_P` to 2.0 without Optical Flow | **Status:** FATAL CRASH (Flipped 180 deg).
- **Fix:** Keep `PSC_POSXY_P = 1.0`. Use 10Hz MAVLink Message #84 Strict Lock instead of internal PID tuning.

## Current To-Do List
1. Test the 1-meter Strict Lock MAVLink python script.
2. Build OpenCV Red Color Detection script for ISRO Task 3.