# Pizza API Example Boundary

`pizzaapi` is included in this workspace as a reference example only.

The analogy is simple:

- `pizzaapi` models an order before sending it to an API transport
- `nsigii-smtp` models a humanitarian request before sending it to SMTP

What `nsigii-smtp` does **not** do:

- import `pizzaapi` in runtime package code
- depend on Domino's APIs
- place food orders directly through business logic

This keeps the NSIGII package aligned with its constitutional purpose: food,
water, shelter, and related aid requests are represented as structured messages,
not as hardwired calls to third-party ordering systems.
