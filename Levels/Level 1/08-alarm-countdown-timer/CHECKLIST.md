# Checklist — 08-alarm-countdown-timer

## Implementation Order
- [ ] Cancel/snooze (2/5)
- [ ] Countdown loop and notifications (1/5)
- [ ] Multiple alarms (2/5)
- [ ] Parse 'HH:MM' or durations (e.g., 10m, 1h) (2/5)

## Tasks

- [ ] Cancel/snooze (2/5)
  - [ ] User can cancel or snooze safely

- [ ] Countdown loop and notifications (1/5)
  - [ ] Accurate countdown within 1s

- [ ] Multiple alarms (2/5)
  - [ ] Run multiple without blocking UI

- [ ] Parse 'HH:MM' or durations (e.g., 10m, 1h) (2/5)
  - [ ] Invalid times rejected; tests

## Bonus

- [ ] Persist alarms to JSON (1/5)
  - [ ] Alarms restored on restart

- [ ] Natural language times (3/5)
  - [ ] 'in 5 minutes' works predictably

- [ ] System notifications/sounds (2/5)
  - [ ] Works on macOS/Win/Linux (documented)
