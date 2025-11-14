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

> 15 = 2 + ! ( 12 * 13 )
OK
> SET 13
OK
> 15
OK
1
> LIST
OK
Pin(15) = 2 + ! ( 12 * 13 )
> 15 = x
OK
> LIST
OK
NONE
> RESET
OK