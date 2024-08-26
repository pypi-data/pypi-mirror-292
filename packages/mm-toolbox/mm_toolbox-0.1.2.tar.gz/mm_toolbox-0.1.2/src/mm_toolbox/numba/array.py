import numpy as np
from numba import njit
from numba.types import bool_
from typing import Tuple, Union


@njit
def nblinspace(start: float, stop: float, num: int = 50) -> np.ndarray:
    return np.linspace(start, stop, num)


@njit
def nbgeomspace(start: float, stop: float, num: int = 50) -> np.ndarray:
    return np.geomspace(start, stop, num)


@njit
def nbarange(start: float, stop: float = None, step: float = 1) -> np.ndarray:
    return np.arange(start, stop, step)


@njit
def nblogspace(start: float, stop: float, num: int = 50) -> np.ndarray:
    return np.logspace(start, stop, num)


@njit
def nbzeros(
    shape: Union[int, Tuple[int, ...]], dtype: np.dtype = np.float64
) -> np.ndarray:
    return np.zeros(shape, dtype)


@njit
def nbones(
    shape: Union[int, Tuple[int, ...]], dtype: np.dtype = np.float64
) -> np.ndarray:
    return np.ones(shape, dtype)


@njit
def nbfull(
    shape: Union[int, Tuple[int, ...]], fill_value: float, dtype: np.dtype = np.float64
) -> np.ndarray:
    return np.full(shape, fill_value, dtype)


@njit
def nbeye(
    N: int, M: int = None, k: int = 0, dtype: np.dtype = np.float64
) -> np.ndarray:
    return np.eye(N, M, k, dtype)


@njit
def nbdiag(v: np.ndarray, k: int = 0) -> np.ndarray:
    return np.diag(v, k)


@njit(inline="always")
def nbisin(a: np.ndarray, b: np.ndarray) -> np.ndarray[bool]:
    """
    Constaints:
    * 'a': dim=1, dtype='same as other'
    * 'b': dim=1, dtype='same as other'
    """
    assert a.ndim == 1 and b.ndim == 1, "2D arrays not supported."

    b_set = set(b)
    out_len = a.size
    out = np.empty(out_len, dtype=bool_)
    for i in range(out_len):
        out[i] = a[i] in b_set

    return out


@njit(inline="always")
def nbwhere(condition, x=None, y=None) -> np.ndarray:
    return np.where(condition, x, y)


@njit(inline="always")
def nbdiff(a: np.ndarray, n: int = 1) -> np.ndarray:
    """
    Constaints:
    * 'a': dim=1, dtype='any numba supported'
    * 'n': dim=1, dtype=int, value='>=0'.
    """

    assert n >= 0 and a.ndim == 1

    if n == 0:
        return a.copy()

    a_size = a.size
    out_size = max(a_size - n, 0)
    out = np.empty(out_size, dtype=a.dtype)

    if out_size == 0:
        return out

    work = np.empty_like(a)

    # First iteration: diff a into work
    for i in range(a_size - 1):
        work[i] = a[i + 1] - a[i]

    # Other iterations: diff work into itself
    for niter in range(1, n):
        for i in range(a_size - niter - 1):
            work[i] = work[i + 1] - work[i]

    # Copy final diff into out
    out[:] = work[:out_size]

    return out


@njit(inline="always")
def nbflip(a: np.ndarray) -> np.ndarray:
    return np.flip(a)


@njit(inline="always")
def nbsort(a: np.ndarray) -> np.ndarray:
    return np.sort(a)


@njit(inline="always")
def nbargsort(a: np.ndarray) -> np.ndarray:
    return np.argsort(a)


@njit(inline="always")
def nbconcatenate(arrays: Tuple[np.ndarray, ...]) -> np.ndarray:
    return np.concatenate(arrays)


@njit(inline="always")
def nbravel(a: np.ndarray) -> np.ndarray:
    return np.ravel(a)


@njit(inline="always")
def nbreshape(a: np.ndarray, newshape: Tuple[int, ...]) -> np.ndarray:
    return np.reshape(a, newshape)


@njit(inline="always")
def nbtranspose(a: np.ndarray) -> np.ndarray:
    return np.transpose(a)


@njit(inline="always")
def nbstack(tup: Tuple[np.ndarray, ...], axis: int) -> np.ndarray:
    return np.stack(tup, axis)


@njit(inline="always")
def nbhstack(tup: Tuple[np.ndarray, ...]) -> np.ndarray:
    return np.hstack(tup)


@njit(inline="always")
def nbvstack(tup: Tuple[np.ndarray, ...]) -> np.ndarray:
    return np.vstack(tup)


@njit(inline="always")
def nbclip(a: np.ndarray, a_min: float, a_max: float) -> np.ndarray:
    return np.clip(a, a_min, a_max)


@njit(inline="always")
def nbunique(a: np.ndarray) -> np.ndarray:
    return np.unique(a)


@njit(inline="always")
def nbrepeat(a: np.ndarray, repeats: Union[int, np.ndarray]) -> np.ndarray:
    return np.repeat(a, repeats)


@njit(inline="always")
def nbroll(a: np.ndarray, shift: int, axis: int) -> np.ndarray:
    assert axis >= 0, "Axis must be positive."

    if shift == 0:
        return a

    if a.ndim == 1:
        if shift > 0:
            return np.concat((a[-shift:], a[:-shift]))
        else:
            return np.concat((a[shift:], a[:shift]))

    # Numba throws index error without this. Seems that it cant
    # infer the early return from ndim==1 branch and fails to
    # generate the memory map correctly for 'a'.
    assert a.ndim > 1

    shift = shift % a.shape[axis]

    out = np.empty_like(a)
    axis_len = a.shape[axis]

    # Roll the array
    for i in range(axis_len):
        new_index = (i + shift) % axis_len
        if axis == 0:
            out[new_index, :] = a[i, :]
        else:
            out[:, new_index] = a[:, i]

    return out
