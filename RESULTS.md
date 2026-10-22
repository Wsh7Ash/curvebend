# Results
- tests: PASS (10 passed)
- bug fixed during build: attack_rate returned an absolute count instead of a fraction (Curve now stores population and divides by it); one test asserted peak_infected on a Scenario instead of a simulated Curve
- cli demo: PASS (60 pct lockdown starting day 5, before the ~day-27 peak: peak drops 48090 -> 15706 and peak day shifts 27.3 -> 97.3; attack rate 99.3% -> 95.9%. A day-30 start leaves the peak unchanged and only trims attack rate, illustrating intervention timing)
