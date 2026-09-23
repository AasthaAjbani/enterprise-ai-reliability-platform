from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PRODUCTION_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production_corrupted.csv"
)


# ---------------------------------------------------------
# 2. EXPECTED SCHEMA
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
    "transaction_id",
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "payment_method",
    "device_type",
    "customer_location",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
    "is_fraud",
]


# ---------------------------------------------------------
# 3. VALID CATEGORIES
# ---------------------------------------------------------

VALID_PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
]

VALID_DEVICE_TYPES = [
    "Mobile",
    "Desktop",
    "Tablet",
]

VALID_LOCATIONS = [
    "Jaipur",
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Pune",
    "Ahmedabad",
]


# ---------------------------------------------------------
# 4. CHECK MISSING COLUMNS
# ---------------------------------------------------------

def check_missing_columns(data):

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in data.columns
    ]

    return missing_columns


# ---------------------------------------------------------
# 5. CHECK MISSING VALUES
# ---------------------------------------------------------

def check_missing_values(data):

    missing_report = (
        data.isnull()
        .sum()
    )

    issues = {}

    for column, count in missing_report.items():

        if count > 0:

            issues[column] = int(count)

    return issues


# ---------------------------------------------------------
# 6. CHECK DUPLICATE TRANSACTION IDs
# ---------------------------------------------------------

def check_duplicates(data):

    duplicate_count = (
        data["transaction_id"]
        .duplicated()
        .sum()
    )

    return int(duplicate_count)


# ---------------------------------------------------------
# 7. CHECK NUMERICAL RULES
# ---------------------------------------------------------

def check_numerical_rules(data):

    issues = {}


    invalid_age = data[
        (data["customer_age"] < 18)
        |
        (data["customer_age"] > 100)
    ]

    if len(invalid_age) > 0:

        issues["customer_age"] = len(
            invalid_age
        )


    invalid_amount = data[
        data["transaction_amount"] <= 0
    ]

    if len(invalid_amount) > 0:

        issues["transaction_amount"] = len(
            invalid_amount
        )


    invalid_hour = data[
        (data["transaction_hour"] < 0)
        |
        (data["transaction_hour"] > 23)
    ]

    if len(invalid_hour) > 0:

        issues["transaction_hour"] = len(
            invalid_hour
        )


    invalid_account_age = data[
        data["account_age_days"] < 0
    ]

    if len(invalid_account_age) > 0:

        issues["account_age_days"] = len(
            invalid_account_age
        )


    invalid_previous_transactions = data[
        data["previous_transactions"] < 0
    ]

    if len(
        invalid_previous_transactions
    ) > 0:

        issues[
            "previous_transactions"
        ] = len(
            invalid_previous_transactions
        )


    invalid_failed_transactions = data[
        data[
            "failed_transactions_last_24h"
        ] < 0
    ]

    if len(
        invalid_failed_transactions
    ) > 0:

        issues[
            "failed_transactions_last_24h"
        ] = len(
            invalid_failed_transactions
        )


    invalid_international = data[
        ~data[
            "is_international"
        ].isin([0, 1])
    ]

    if len(
        invalid_international
    ) > 0:

        issues[
            "is_international"
        ] = len(
            invalid_international
        )


    return issues


# ---------------------------------------------------------
# 8. CHECK CATEGORICAL VALUES
# ---------------------------------------------------------

def check_categorical_rules(data):

    issues = {}


    invalid_payment = data[
        ~data[
            "payment_method"
        ].isin(
            VALID_PAYMENT_METHODS
        )
    ]

    if len(invalid_payment) > 0:

        issues[
            "payment_method"
        ] = len(
            invalid_payment
        )


    invalid_device = data[
        ~data[
            "device_type"
        ].isin(
            VALID_DEVICE_TYPES
        )
    ]

    if len(invalid_device) > 0:

        issues[
            "device_type"
        ] = len(
            invalid_device
        )


    invalid_location = data[
        ~data[
            "customer_location"
        ].isin(
            VALID_LOCATIONS
        )
    ]

    if len(invalid_location) > 0:

        issues[
            "customer_location"
        ] = len(
            invalid_location
        )


    return issues


# ---------------------------------------------------------
# 9. CALCULATE DATA QUALITY SCORE
# ---------------------------------------------------------

def calculate_quality_score(
    total_rows,
    missing_values,
    duplicates,
    numerical_issues,
    categorical_issues,
):

    total_issues = (
        sum(
            missing_values.values()
        )
        +
        duplicates
        +
        sum(
            numerical_issues.values()
        )
        +
        sum(
            categorical_issues.values()
        )
    )


    if total_rows == 0:
        return 0


    issue_ratio = (
        total_issues
        /
        total_rows
    )


    score = (
        100
        -
        issue_ratio * 100
    )


    return max(
        0,
        round(score, 2)
    )


# ---------------------------------------------------------
# 10. DETERMINE STATUS
# ---------------------------------------------------------

def determine_quality_status(
    score,
    missing_columns,
):

    if missing_columns:
        return "CRITICAL"

    if score < 90:
        return "CRITICAL"

    if score < 98:
        return "WARNING"

    return "HEALTHY"


# ---------------------------------------------------------
# 11. MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print(
        "\nLoading production data..."
    )

    data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )

    print(
        "Production data loaded successfully."
    )


    missing_columns = (
        check_missing_columns(
            data
        )
    )


    if missing_columns:

        print(
            "\nCRITICAL SCHEMA ERROR"
        )

        print(
            "Missing columns:"
        )

        for column in missing_columns:

            print(
                f" - {column}"
            )

        return


    missing_values = (
        check_missing_values(
            data
        )
    )


    duplicates = (
        check_duplicates(
            data
        )
    )


    numerical_issues = (
        check_numerical_rules(
            data
        )
    )


    categorical_issues = (
        check_categorical_rules(
            data
        )
    )


    quality_score = (
        calculate_quality_score(
            len(data),
            missing_values,
            duplicates,
            numerical_issues,
            categorical_issues,
        )
    )


    status = (
        determine_quality_status(
            quality_score,
            missing_columns,
        )
    )


    # -----------------------------------------------------
    # DISPLAY REPORT
    # -----------------------------------------------------

    print("\n")
    print("=" * 70)

    print(
        "DATA QUALITY REPORT"
    )

    print("=" * 70)


    print(
        f"\nRows checked: {len(data)}"
    )

    print(
        f"Quality Score: {quality_score}/100"
    )

    print(
        f"Status: {status}"
    )


    print(
        "\nMissing Values:"
    )

    if missing_values:

        for column, count in (
            missing_values.items()
        ):

            print(
                f" - {column}: {count}"
            )

    else:

        print(
            " - None"
        )


    print(
        "\nDuplicate Transaction IDs:"
    )

    print(
        f" - {duplicates}"
    )


    print(
        "\nInvalid Numerical Values:"
    )

    if numerical_issues:

        for column, count in (
            numerical_issues.items()
        ):

            print(
                f" - {column}: {count}"
            )

    else:

        print(
            " - None"
        )


    print(
        "\nInvalid Categorical Values:"
    )

    if categorical_issues:

        for column, count in (
            categorical_issues.items()
        ):

            print(
                f" - {column}: {count}"
            )

    else:

        print(
            " - None"
        )


    print("\n")
    print("=" * 70)


if __name__ == "__main__":
    main()