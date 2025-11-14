# Pin Safety

The following pins are protected to prevent interference with flash memory or serial programming:

| Type         | Pins |
| ------------ | ---- |
| Flash/Debug  | 1, 3 |
| Flash Memory | 6-11 |

Any attempt to use these pins will result in an error.
Furthermore:
- Directly shorting the gates inputs and outputs or duplicating gates will result in error.
- Overwriting output pins will result in the deletion/replacement of gates.
- Add `?` at the end of any command for debug mode to show detailed error messages.

# Example Session

> 15 = 12 + 13
OK
> set 13
OK
> 15
OK
1
> GATES
OK
Pin(15) = Pin(12) + Pin(13)
> 15 = x
OK
> list
OK
NONE
> reset
OK