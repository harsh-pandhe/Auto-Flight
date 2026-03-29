Full backup transfer chunks for auto-flight.

Original archive:
- auto-flight_full_20260330.tar.zst

Reassemble from this directory:
cat auto-flight_full_20260330.tar.zst.part-* > auto-flight_full_20260330.tar.zst

Verify with checksum one level up:
sha256sum -c ../auto-flight_full_20260330.tar.zst.sha256

Extract:
tar -I zstd -xf auto-flight_full_20260330.tar.zst
