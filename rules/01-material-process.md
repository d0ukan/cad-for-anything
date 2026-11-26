# 01 · Material and process (MAT)

- **MAT-01** — Choose the process from quantity, size, load and cost — not
  from habit. Rough guide:

  | Quantity | Typical process |
  | :--- | :--- |
  | 1–20, plastic | FDM, SLA, SLS |
  | 1–100, metal, blocky | CNC milling / turning |
  | 1–1000+, metal, flat/bent | Sheet metal (laser cut + bend) |
  | 1000+, plastic | Injection moulding (out of scope; ask an expert) |

- **MAT-02** — Prototype phase uses FDM. Pick the prototype material close to
  the final one: PLA for fit/shape only, PETG or ABS/ASA for function and heat,
  PA-CF/PETG-CF for stiffness.
- **MAT-03** — Check the environment: max temperature (PLA softens ~55 °C),
  UV/outdoor (use ASA, aluminium, stainless), water, chemicals, food contact.
- **MAT-04** — Default metals unless the user asks otherwise:
  CNC aluminium 6061-T6 (or 6082-T6 in EU); sheet steel DC01 / S235 with
  zinc plating or powder coat; stainless 304 when corrosion matters.
- **MAT-05** — Record material grade, finish and colour in
  `requirements.md`. "Aluminium" alone is not enough.
- **MAT-06** — Use a safety factor of at least 2 on yield for static loads
  (3+ for printed parts, because layer adhesion is weak and data varies).
- **MAT-07** — FDM prototype strength is **not** the final part strength.
  A passed prototype test proves fit and function, not the final load rating.
- **MAT-08** — The prototype keeps every interface of the final part the same:
  hole sizes and positions, mating faces, outer envelope, connector/screw
  types. Only wall thickness, ribs and fillets may change for printing or
  strength. Otherwise the prototype test proves nothing.
