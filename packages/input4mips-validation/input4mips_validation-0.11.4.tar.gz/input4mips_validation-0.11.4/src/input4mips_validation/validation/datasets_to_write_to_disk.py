"""
Validation of datasets that we are writing to disk
"""

from __future__ import annotations

from pathlib import Path

import xarray as xr

from input4mips_validation.cvs import Input4MIPsCVs
from input4mips_validation.validation.creation_date import validate_creation_date
from input4mips_validation.validation.error_catching import get_catch_error_decorator


class InvalidDatasetToWriteToDiskError(ValueError):
    """
    Raised when a dataset to write to disk does not pass all of the validation
    """

    def __init__(
        self,
        ds: xr.Dataset,
        error_container: list[tuple[str, Exception]],
    ) -> None:
        """
        Initialise the error

        Parameters
        ----------
        ds
            The dataset we tried to validate

        error_container
            The thing which was being done
            and the error which was caught
            while validating `ds`.
        """
        error_msgs: list[str] = []
        for error in error_container:
            process, exc = error
            formatted_exc = f"{type(exc).__name__}: {exc}"
            error_msgs.append(f"{process} failed. Exception: {formatted_exc}")

        error_msgs_str = "\n\n".join(error_msgs)

        error_msg = (
            f"Failed to validate {ds=}\n"
            "Caught error messages:\n\n"
            f"{error_msgs_str}"
        )

        super().__init__(error_msg)


def validate_ds_to_write_to_disk(
    ds: xr.Dataset, out_path: Path, cvs: Input4MIPsCVs
) -> None:
    """
    Validate a dataset that is going to be written to disk

    Parameters
    ----------
    ds
        Dataset to write to disk.
        May contain one or more variables.

    out_path
        Path in which to the dataset will be written

    cvs
        CVs to use to validate the dataset before writing

    Raises
    ------
    InvalidDatasetToWriteToDiskError
        Given the values of `out_path` and `cvs`,
        `ds` is not valid for writing to disk.
    """
    caught_errors: list[tuple[str, Exception]] = []
    checks_performed: list[str] = []
    catch_error = get_catch_error_decorator(caught_errors, checks_performed)

    catch_error(
        validate_creation_date, call_purpose="Validate the creation_date attribute"
    )(ds.attrs["creation_date"])

    if caught_errors:
        raise InvalidDatasetToWriteToDiskError(
            ds=ds,
            error_container=caught_errors,
        )
