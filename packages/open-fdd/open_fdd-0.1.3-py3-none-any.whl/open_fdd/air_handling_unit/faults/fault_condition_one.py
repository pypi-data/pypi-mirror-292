import pandas as pd
from open_fdd.air_handling_unit.faults.fault_condition import (
    FaultCondition,
    MissingColumnError,
)
import sys


class FaultConditionOne(FaultCondition):
    """Class provides the definitions for Fault Condition 1.
    AHU low duct static pressure fan fault.
    """

    def __init__(self, dict_):
        super().__init__()
        self.vfd_speed_percent_err_thres = float
        self.vfd_speed_percent_max = float
        self.duct_static_inches_err_thres = float
        self.duct_static_col = str
        self.supply_vfd_speed_col = str
        self.duct_static_setpoint_col = str
        self.troubleshoot_mode = bool  # default should be False
        self.rolling_window_size = int

        self.set_attributes(dict_)

        # Set required columns specific to this fault condition manually
        self.required_columns = [
            self.duct_static_col,
            self.supply_vfd_speed_col,
            self.duct_static_setpoint_col,
        ]

    def get_required_columns(self) -> str:
        """Returns a string representation of the required columns."""
        return f"Required columns for FaultConditionOne: {', '.join(self.required_columns)}"

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Ensure all required columns are present
            self.check_required_columns(df)

            if self.troubleshoot_mode:
                self.troubleshoot_cols(df)

            # Check analog outputs [data with units of %] are floats only
            columns_to_check = [self.supply_vfd_speed_col]
            self.check_analog_pct(df, columns_to_check)

            df["static_check_"] = (
                df[self.duct_static_col]
                < df[self.duct_static_setpoint_col] - self.duct_static_inches_err_thres
            )
            df["fan_check_"] = (
                df[self.supply_vfd_speed_col]
                >= self.vfd_speed_percent_max - self.vfd_speed_percent_err_thres
            )

            # Combined condition check
            df["combined_check"] = df["static_check_"] & df["fan_check_"]

            # Rolling sum to count consecutive trues
            rolling_sum = (
                df["combined_check"].rolling(window=self.rolling_window_size).sum()
            )
            # Set flag to 1 if rolling sum equals the window size
            df["fc1_flag"] = (rolling_sum == self.rolling_window_size).astype(int)

            if self.troubleshoot_mode:
                print("Troubleshoot mode enabled - not removing helper columns")
                sys.stdout.flush()
                del df["static_check_"]
                del df["fan_check_"]
                del df["combined_check"]

            return df

        except MissingColumnError as e:
            print(f"Error: {e.message}")
            sys.stdout.flush()
            raise e  # Re-raise the exception so it can be caught by pytest
