"""
Utility to calculate option prices or implied volatility surface from a MC Simulation, for any model.
This is useful for calibrating the model to Black-Scholes option prices.
"""

import numpy as np

from finmc.models.base import MCBase
from finmc.utils.bs import impliedvol


def iv_surface_mc(
    strikes,
    expirations,  # in years, increasing order
    asset_name: str,
    model: MCBase,
):
    """Calculate the implied volatility surface using MC Simulation.

    Args:
        strikes: The strikes of the options.
        expirations: The expirations of the options in years.
        asset_name: The name of the asset.
        model: The model used to simulate the asset price.

    Returns:
        A tuple containing the implied volatility surface, the ATM volatilities, and the forward prices.

    Examples:
        surface, atm_vols, fwds = iv_surface_mc(Ks, Ts, "SPX", model)
    """

    iv_mat = np.zeros((len(expirations), len(strikes)))
    iv_atm = []
    fwds = []
    model.reset()
    for i, exp in enumerate(expirations):
        model.advance(exp)
        expiration_spots = model.get_value(asset_name)
        fwd = expiration_spots.mean()

        # Use a call option for strikes above forward, a put option otherwise
        is_call = strikes > fwd
        is_call_c = is_call[..., None]  # Turn into a column vector

        # calculate prices (value as of expiration date)
        strikes_c = strikes[..., None]  # Turn into a column vector
        pay = np.where(
            is_call_c,
            expiration_spots - strikes_c,
            strikes_c - expiration_spots,
        )
        prices = np.maximum(pay, 0).mean(axis=1)

        # calculate implied vols
        iv_mat[i, :] = [
            impliedvol(p, fwd, k, exp, ic)
            for p, k, ic in zip(prices, strikes, is_call)
        ]

        # calculate atm vols
        atm_call = np.maximum(expiration_spots - fwd, 0).mean()
        # calculate implied vols and fwds
        fwds.append(fwd)
        iv_atm.append(impliedvol(atm_call, fwd, fwd, exp, True))
    return iv_mat, np.array(iv_atm), np.array(fwds)


if __name__ == "__main__":
    import pandas as pd

    from finmc.models.localvol import LVMC

    # create the dataset
    dataset = {
        "MC": {"PATHS": 100_000, "TIMESTEP": 1 / 10},
        "BASE": "USD",
        "ASSETS": {
            "USD": ("ZERO_RATES", np.array([[1.0, 0.04]])),
            "SPX": ("FORWARDS", np.array([[0.0, 2900], [1.0, 3000]])),
        },
        "LV": {
            "ASSET": "SPX",
            "VOL": 0.3,
        },
    }

    # create the model and calculate the implied volatility surface
    model = LVMC(dataset)
    strikes = np.linspace(2900, 3100, 3)
    expirations = [1 / 12, 1 / 6, 1 / 4, 1 / 2, 1]
    surface, atm_vols, fwds = iv_surface_mc(
        strikes,
        expirations,
        asset_name="SPX",
        model=model,
    )
    # print the surface as a DataFrame
    df = pd.DataFrame(surface, columns=strikes, index=expirations)
    print(f"surface:\n{df}")
    print(f"atm_vols:\n{atm_vols}")
    print(f"fwds:\n{fwds}")
