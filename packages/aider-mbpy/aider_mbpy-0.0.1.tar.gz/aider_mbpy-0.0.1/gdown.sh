#!/bin/bash

# urls=(
#   "https://drive.google.com/uc?id=1fq4G5djBblr6FME7TY5WH7Lnz9psVf4i"
#   "https://drive.google.com/uc?id=1bj1rEpCJR7qYZ2u8ZQ4AA475wcCrZ5rV"
#   "https://drive.google.com/uc?id=1WzcIm2G55yTh-snOrdeiZJrYDBqJeAck"
#   "https://drive.google.com/uc?id=1ezXXY_ZK7PtTBDtk9yA4e1og-oNQqhfy"
#   "https://drive.google.com/uc?id=1ENNc792YoI6SEQb_TO7cqUElPeDMAE6H"
#   "https://drive.google.com/uc?id=1K-qCfHamkgUdbJUK80bJTQzh-m2kn9ST"
#   "https://drive.google.com/uc?id=1hBXc2WBAc59rS6hbjwvKWQwAD7cGsLp5"
#   "https://drive.google.com/uc?id=1SiDvd6ivYSJS_-Bvo96g5nR-Gl-2843z"
# )

urls=(
  "https://drive.google.com/uc?id=1SiDvd6ivYSJS_-Bvo96g5nR-Gl-2843z",
  "https://drive.google.com/uc?id=1hBXc2WBAc59rS6hbjwvKWQwAD7cGsLp5",
  "https://drive.google.com/uc?id=1K-qCfHamkgUdbJUK80bJTQzh-m2kn9ST",
  "https://drive.google.com/uc?id=1ENNc792YoI6SEQb_TO7cqUElPeDMAE6H",
  "https://drive.google.com/uc?id=1ezXXY_ZK7PtTBDtk9yA4e1og-oNQqhfy",
  "https://drive.google.com/uc?id=1WzcIm2G55yTh-snOrdeiZJrYDBqJeAck",
  "https://drive.google.com/uc?id=1bj1rEpCJR7qYZ2u8ZQ4AA475wcCrZ5rV",
  "https://drive.google.com/uc?id=1fq4G5djBblr6FME7TY5WH7Lnz9psVf4i",
)

for url in "${urls[@]}"; do
  gdown  https://drive.google.com/uc?id=1SiDvd6ivYSJS_-Bvo96g5nR-Gl-2843z
done
