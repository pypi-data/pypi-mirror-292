class _SIZES:
    def __init__(self, sizes) -> None:
        for name, size_dict in sizes.items():
            setattr(self, name, size_dict)


ACS_Sizes = _SIZES(
    {
        "single_column": {
            "mm": 82.55,
            "in": 3.25,
            "cm": 8.255,
        },
        "double_column": {
            "mm": 177.8,
            "in": 7,
            "cm": 17.78,
        },
    }
)

Elsevier_Sizes = _SIZES(
    {
        "single_column": {
            "mm": 90,
            "in": 3.54,
            "cm": 9,
        },
        "threehalf_column": {
            "mm": 140,
            "in": 5.51,
            "cm": 14,
        },
        "double_column": {
            "mm": 190,
            "in": 7.48,
            "cm": 19,
        },
    }
)

if __name__ == "__main__":
    print(ACS_Sizes.single_column["cm"])
    print(Elsevier_Sizes.single_column)
    print(Elsevier_Sizes.threehalf_column)
    print(Elsevier_Sizes.double_column)
    print(ACS_Sizes.double_column)
