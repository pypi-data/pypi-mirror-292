import decimal as dc

import numpy as np
from tqdm import tqdm  # for progress bar


# from numerical_function_spaces.orlicz_spaces.orlicz_functions import *


def kappa(Orlicz_function, x, k, p_norm):
    """
    Calculates the kappa value for a given set of parameters.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    x : np.ndarray
        A 2D numpy array representing x(t).
    k : float
        must be positive.
    p_norm : float
        The p-norm to be calculated.

    Returns
    -------
    The kappa value : np.float64.

    Raises
    ------
    ValueError: If x[1, :] contains non-positive values.

    Examples
    --------
    >>> x = np.array([[1],[1]])
    >>> def Orlicz_function(u):
    ...     return u
    ...
    >>> kappa(Orlicz_function, x=x, k=1, p_norm=1)
    np.float64(2.0)
    """
    # x_abs = np.zeros(shape=np.shape(x))  # x[0, :] = abs(x[0, :]) powoduje zmianę zewnętrznej zmiennej!!! ???
    # x_abs[0, :] = abs(x[0, :])
    # x_abs[1, :] = x[1, :]
    if any(x[1, :] <= 0):
        raise ValueError("wrong definition of x(t): x[1, :] must be positive")
    x = abs(x)
    # np.nansum dopuszcza wagi nieskończone przyjmujemy wtedy, że 0*inf = 0. Numpy przyjmuje, że to jest Nan
    if p_norm == 1:
        return 1 / k * (1 + np.nansum(Orlicz_function((k * x[0, :])) * x[1, :]))
    elif p_norm == np.inf:
        return 1 / k * (max(1, np.nansum(Orlicz_function((k * x[0, :])) * x[1, :])))
    else:
        return 1 / k * (1 + (np.nansum(Orlicz_function((k * x[0, :])) * x[1, :]) ** p_norm)) ** (1 / p_norm)


def p_Amemiya_norm(
        Orlicz_function,
        x: np.ndarray,
        p_norm: float):
    """
   Calculates the p_Amemiya norm for a given set of parameters.

   Parameters
   ----------
   Orlicz_function : function
       The Orlicz function to be used.
   x : np.ndarray
       A 2D numpy array representing x(t).
   p_norm : float
       The p-norm to be calculated.

   Returns
   -------
   value of the p-Amemiya norm : np.float64.

   Raises
   ------
   ValueError: If x[1, :] contains non-positive values.

   Examples
   --------
   >>> x = np.array([[1],[1]])
   >>> def Orlicz_function(u):
   ...     return u
   ...
   >>> p_Amemiya_norm(Orlicz_function, x=x, p_norm=1)
   np.float64(1.0)
   """
    val_k = np.empty([2, 5])  # domain and values kappa - for looking minimum
    val_k[:] = None
    val_k[1, 0] = 1
    val_k[1, 1] = 2
    val_k[1, 2] = 4
    val_k[1, 3] = 8
    val_k[1, 4] = 16
    for i in range(5):
        val_k[0, i] = kappa(Orlicz_function, x, k=val_k[1, i], p_norm=p_norm)
    # print(np.nanmin(val_k[0]))
    # print(np.nanargmin(val_k[0]))
    # print(val_k)
    for i in range(100):
        if np.nanargmin(val_k[0]) == 0:
            # print('pierwszy najmniejszy')
            val_k[:, 4] = val_k[:, 3]
            val_k[:, 3] = val_k[:, 2]
            val_k[:, 2] = val_k[:, 1]
            val_k[:, 1] = val_k[:, 0]
            val_k[1, 0] = (val_k[1, 1]) / 2
            val_k[0, 0] = kappa(Orlicz_function, x, k=val_k[1, 0], p_norm=p_norm)
        elif np.nanargmin(val_k[0]) == 1:
            # print('drugi najmniejszy')
            val_k[:, 4] = val_k[:, 3]
            val_k[:, 3] = val_k[:, 2]
            val_k[:, 2] = val_k[:, 1]
            val_k[1, 1] = (val_k[1, 0] + val_k[1, 2]) / 2
            val_k[0, 1] = kappa(Orlicz_function, x, k=val_k[1, 1], p_norm=p_norm)
        elif np.nanargmin(val_k[0]) == 2:
            # print('trzeci najmniejszy')
            val_k[:, 4] = val_k[:, 3]
            val_k[:, 3] = val_k[:, 2]
            val_k[1, 2] = (val_k[1, 1] + val_k[1, 3]) / 2
            val_k[0, 2] = kappa(Orlicz_function, x, k=val_k[1, 2], p_norm=p_norm)
        elif np.nanargmin(val_k[0]) == 3:
            # print('czwarty najmniejszy')
            val_k[:, 0] = val_k[:, 1]
            val_k[:, 1] = val_k[:, 2]
            val_k[:, 2] = val_k[:, 3]
            val_k[1, 3] = (val_k[1, 2] + val_k[1, 4]) / 2
            val_k[0, 3] = kappa(Orlicz_function, x, k=val_k[1, 3], p_norm=p_norm)
        else:
            # print('ostatni najmniejszy')
            val_k[:, 0] = val_k[:, 1]
            val_k[:, 1] = val_k[:, 2]
            val_k[:, 2] = val_k[:, 3]
            val_k[:, 3] = val_k[:, 4]
            val_k[1, 4] = val_k[1, 3] * 2
            val_k[0, 4] = kappa(Orlicz_function, x, k=val_k[1, 4], p_norm=p_norm)
            # print(f'{np.nanmin(val_k[0]):.16}')
        # print(np.nanargmin(val_k[0]))
        # print(val_k)
    return np.nanmin(val_k[0])


# array_for_infimum was replaced by kappa
# def array_for_infimum( # tego chyba nie używamy
#         Orlicz_function,
#         x: np.ndarray,
#         # dt: float,
#         k_min: float,
#         k_max: float,
#         dk: float,
#         p_norm: float,
#         show_progress: bool = False
# ) -> tuple:
#     x = abs(x)
#     domain_k = np.arange(k_min, k_max, dk)
#     array_k = np.array([])
#     if p_norm == 1:
#         with tqdm(
#                 total=len(domain_k),
#                 # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
#                 # desc="counting of  $1/k*s_p(I_phi)(kx)$ in [" + str(k_min) + "," + str(k_max) + "]",
#                 desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
#                 disable=not show_progress
#         ) as pbar:
#             for k in domain_k:
#                 array_k = np.append(
#                     array_k,
#                     1 / k * (1 + np.nansum(Orlicz_function((k * x[0])) * x[1])),
#                 )
#                 pbar.update(1)
#     elif p_norm == np.inf:
#         with tqdm(
#                 total=len(domain_k),
#                 # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
#                 desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
#                 disable=not show_progress
#         ) as pbar:
#             for k in domain_k:
#                 array_k = np.append(
#                     array_k,
#                     1
#                     / k
#                     * (
#                         max(
#                             1,
#                             np.nansum(Orlicz_function((k * x[0])) * x[1]),
#                         )
#                     ),
#                 )
#                 pbar.update(1)
#     else:
#         with tqdm(
#                 total=len(domain_k),
#                 # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
#                 desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
#                 disable=not show_progress
#         ) as pbar:
#             for k in domain_k:
#                 array_k = np.append(
#                     array_k,
#                     1
#                     / k
#                     * (
#                             1
#                             + (
#                                     np.nansum(Orlicz_function((k * x[0])) * x[1])
#                                     ** p_norm
#                             )
#                     )
#                     ** (1 / p_norm),
#                 )
#                 pbar.update(1)
#     # print(array_k)
#     return domain_k, array_k


def Orlicz_norm_with_stars(
        Orlicz_function,
        x: np.ndarray,
        # dt: float,
        k_min: float = 0.000001,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
):
    """
    Computes the Orlicz norm and k^{*} and k^{**} of the function "x(t)"
    in Orlicz space for a given set of parameters as p_Amimiya norm for p_norm=1

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    x : np.ndarray
        A 2D numpy array representing x(t).
    k_min : float, optional
        The minimum value of the k domain, by default 0.000001.
    k_max : float, optional
        The maximum value of the k domain, by default 100.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default, False.

    Returns
    -------
    - A tuple containing the value of the Orlicz norm, k^{*}, k^{**}.

    Examples
    --------
        >>> x = np.array([[1],[2]])
        >>> def Orlicz_function(u):
        ...     return np.where(u <= 1, 0, u - 1)
        ...
        >>> Orlicz_norm_with_stars(Orlicz_function, x)
        (np.float64(1.000008302431002), np.float64(1.0000083024999329), np.float64(1.0000083024999329))
    """
    # return p_Amemiya_norm_with_stars(Orlicz_function, x, dt, 1, k_min, k_max, len_domain_k,
    #                                  show_progress=show_progress)
    return p_Amemiya_norm_with_stars(Orlicz_function, x, 1, k_min, k_max, dk, len_domain_k,
                                     show_progress=show_progress)


def Luxemburg_norm_with_stars(
        Orlicz_function,
        x: np.ndarray,
        # dt: float,
        k_min: float = 0.000001,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
):
    """
    Computes the Luxemburg norm and k^{*} and k^{**} of the function "x(t)"
    in Orlicz space for a given set of parameters as p_Amimiya norm for p_norm=np.inf

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    x : np.ndarray
        A 2D numpy array representing x(t).
    k_min : float, optional
        The minimum value of the k domain, by default 0.000001.
    k_max : float, optional
        The maximum value of the k domain, by default 100.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default, False.

    Returns
    -------
    - A tuple containing the value of the Luxemburg norm, k^{*}, k^{**}.

    Examples
    --------
        >>> x = np.array([[1],[2]])
        >>> def Orlicz_function(u):
        ...     return np.where(u <= 1, 0, u - 1)
        ...
        >>> Luxemburg_norm_with_stars(Orlicz_function, x)
        (np.float64(0.666712308582787), np.float64(1.4998973127189956), np.float64(1.4998973127189956))
    """
    # return p_Amemiya_norm_with_stars(Orlicz_function, x, dt, np.inf, k_min, k_max, len_domain_k,
    #                                  show_progress=show_progress)
    return p_Amemiya_norm_with_stars(Orlicz_function, x, np.inf, k_min, k_max, dk, len_domain_k,
                                     show_progress=show_progress)


def p_Amemiya_norm_with_stars(
        Orlicz_function,
        x: np.ndarray,
        # dt: float,
        p_norm: float,
        k_min: float = 0.000001,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
):
    """
    Computes the p-Amemiya norm and k^{*} and k^{**} of the function "x(t)"
    in Orlicz space for a given set of parameters

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated.
    k_min : float, optional
        The minimum value of the k domain, by default 0.000001.
    k_max : float, optional
        The maximum value of the k domain, by default 100.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default, False.

    Returns
    -------
    A tuple containing the value of the p-Amemiya norm, k^{*}, k^{**}.

    Note
    ----
    Precision problem with k^{*} false less than k^{**} for Phi = max(u,2u-1), x=chi_(0,3), p=20.
    Too small accuracy.

    Problem eliminated in slower function p_Amemiya_norm_with_stars_by_decimal().

    Examples
    --------
        >>> x = np.array([[1],[1]])
        >>> def Orlicz_function(u):
        ...     return u**2
        ...
        >>> p_Amemiya_norm_with_stars(Orlicz_function, x=x, p_norm=1)
        (np.float64(2.000000000068931), np.float64(1.0000083024999067), np.float64(1.0000083024999067))
    """

    if any(x[1, :] <= 0):
        raise ValueError("wrong definition of x(t): x[1, :] must be positive")
    x = abs(x)
    if np.max(x) == 0:
        return 0, np.nan, np.nan
    # k_min = 0.000001
    # k_max = 100
    # len_domain_k = 1000
    if dk is None:  # if len_domain_k is specified by user
        dk = (k_max - k_min) / len_domain_k
    else:
        len_domain_k == (k_max - k_min) * dk

    # domain_k = np.arange(k_min, k_max, dk)
    # print("k_min = ", k_min, ",k_max= ", k_max)
    # domain_k, array_k = array_for_infimum(
    #     Orlicz_function, x, dt, k_min, k_max, dk, p_norm, show_progress=show_progress
    # )
    # domain_k, array_k = array_for_infimum(
    #     Orlicz_function, x, k_min, k_max, dk, p_norm, show_progress=show_progress
    # )
    domain_k = np.arange(k_min, k_max, dk)
    array_k = np.array([])
    with tqdm(
            total=len(domain_k),
            # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
            # desc="counting of  $1/k*s_p(I_phi)(kx)$ in [" + str(k_min) + "," + str(k_max) + "]",
            desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
            disable=not show_progress
    ) as pbar:
        for k in domain_k:
            array_k = np.append(array_k, kappa(Orlicz_function, x, k, p_norm))
            pbar.update(1)

    # Todo: precision problem with k^* false less than k^** for Phi = max(u,2u-1), x=chi_(0,3), p=10. too small accuracy.
    accuracy = max((np.max(array_k[np.isfinite(array_k)])
                    - np.min(array_k[np.isfinite(array_k)])) * 0.000001, 1e-15)
    osiagane_minimum = np.where(
        np.logical_and(
            # array_k < array_k[np.argmin(array_k)] + 0.00001,
            # array_k > array_k[np.argmin(array_k)] - 0.00001,
            array_k < array_k[np.argmin(array_k)] + accuracy,
            array_k > array_k[np.argmin(array_k)] - accuracy,
        )
    )
    # print(accuracy)
    # print(osiagane_minimum)
    # k_star = domain_k[np.min(osiagane_minimum) - 1]
    k_star = domain_k[np.min(osiagane_minimum)]
    # k_star_star = domain_k[np.max(osiagane_minimum) + 1]
    k_star_star = domain_k[np.max(osiagane_minimum)]
    # print(f"||x||={min(array_k)}, k^*={k_star}, k^(**)={k_star_star}")
    ''' for default values, try to count more precisely '''
    ''' Problem with k^**=infinity and k^*=1 - 
    wrong calculations '''
    if k_min == 0.000001 and k_max == 100 and len_domain_k == 1000:
        for licz in range(4):
            # print(licz)
            # print("||x||=", min(array_k))
            # print("k_min = ", k_min, ",k_max= ", k_max)
            if (
                    np.max(
                        np.where(array_k < array_k[np.argmin(array_k)] + 0.00001)
                    )
                    == len(domain_k) - 1
            ):
                if licz == 1:  # po do to jest? przy pierwszym wejściu jest licz = 0.
                    pass  # 14.07.2024 wcześniej było break, ale wyrzucało po jednym wejściu do pętli
                else:
                    k_min = 0.5 * (k_min + domain_k[
                        np.min(
                            np.where(
                                array_k
                                < np.min(array_k) + 0.00001
                            )
                        )
                    ]
                                   )
                # print(k_min,np.min(array_k),
                #       np.min(domain_k[np.where(array_k < (np.min(array_k) + 0.00001))]))
                k_max = 10 * k_max
                len_domain_k = 10 * len_domain_k
            else:
                parametr = (0.5 ** (licz + 1)) * (
                    max(
                        domain_k[
                            np.min(
                                np.where(
                                    array_k
                                    < np.min(array_k) + 0.00001
                                )
                            )
                        ]
                        - k_min,
                        k_max
                        - domain_k[
                            np.max(
                                np.where(
                                    array_k
                                    < np.min(array_k) + 0.00001
                                )
                            )
                        ],
                    )
                )
                k_min = max(
                    k_min,
                    domain_k[
                        np.min(
                            np.where(
                                array_k
                                < np.min(array_k) + 0.00001
                            )
                        )
                    ]
                    - parametr,
                )
                k_max = min(
                    k_max,
                    domain_k[
                        np.max(
                            np.where(
                                array_k
                                < np.min(array_k) + 0.00001
                            )
                        )
                    ]
                    + parametr,
                )
            # print(domain_k[np.min(np.where(array_k < array_k[np.argmin(array_k)]+0.00001*0.1**licz))])
            # print(domain_k[np.max(np.where(array_k < array_k[np.argmin(array_k)]+0.00001*0.1**licz))])
            dk = (k_max - k_min) / len_domain_k
            # domain_k = np.arange(k_min, k_max, dk)
            # domain_k, array_k = array_for_infimum(
            #     Orlicz_function, x, dt, k_min, k_max, dk, p_norm, show_progress=show_progress
            # )
            # domain_k, array_k = array_for_infimum(
            #     Orlicz_function, x, k_min, k_max, dk, p_norm, show_progress=show_progress
            # )
            domain_k = np.arange(k_min, k_max, dk)
            array_k = np.array([])
            with tqdm(
                    total=len(domain_k),
                    # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
                    # desc="counting of  $1/k*s_p(I_phi)(kx)$ in [" + str(k_min) + "," + str(k_max) + "]",
                    desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
                    disable=not show_progress
            ) as pbar:
                for k in domain_k:
                    array_k = np.append(array_k, kappa(Orlicz_function, x, k, p_norm))
                    pbar.update(1)
            accuracy = max((np.max(array_k[np.isfinite(array_k)])
                            - np.min(array_k[np.isfinite(array_k)])) * 0.000001, 1e-15)
            osiagane_minimum = np.where(
                np.logical_and(
                    # array_k < array_k[np.argmin(array_k)] + 0.00001,
                    # array_k > array_k[np.argmin(array_k)] - 0.00001,
                    array_k < array_k[np.argmin(array_k)] + accuracy,
                    array_k > array_k[np.argmin(array_k)] - accuracy,
                )
            )
            # print(accuracy)
            # print(osiagane_minimum)
            # k_star = domain_k[np.min(osiagane_minimum) - 1]
            k_star = domain_k[np.min(osiagane_minimum)]
            # k_star_star = domain_k[np.max(osiagane_minimum) + 1]
            k_star_star = domain_k[np.max(osiagane_minimum)]
            if k_max >= 10000:
                print('\n\x1b[41m Time to consider infinity\x1b[0m ')
                break
            # print(f"||x||={min(array_k)}, k^*={k_star}, k^(**)={k_star_star}")
    ''' above problem with k^**=infinity and k^*=1 - '''
    # print(array_k)
    # print(np.nanmin(osiagane_minimum), np.nanmax(osiagane_minimum))
    if np.min(osiagane_minimum) == 0:
        print('k_star is equal to k_min: try smaller k_min')
    if np.max(osiagane_minimum) == len(domain_k) - 1:
        print('k_star_star is equal to k_max: try larger k_max')
    return min(array_k), k_star, k_star_star  # , domain_k, array_k


def p_Amemiya_norm_with_stars_by_decimal(
        Orlicz_function,
        x: np.ndarray,
        # dt: float,
        p_norm: dc.Decimal,
        k_min: dc.Decimal = dc.Decimal(1) / 100000,
        k_max: dc.Decimal = dc.Decimal(100),
        dk: dc.Decimal = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
) -> tuple:
    """
    Computes the p-Amemiya norm and k^{*} and k^{**} of the function "x(t)"
    in Orlicz space for a given set of parameters

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated (in decimal form).
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 1/100000.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 100.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain in decimal form, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.

    Returns
    -------
    A tuple containing the minimum value of the p-Amemiya norm, k^{*}, k^{**}, kappa_domain, and kappa_values.

    Raises
    ------
    - ValueError: If any value in x[1, :] is less than or equal to 0.

    Examples
    --------
        >>> x = np.array([[1], [2]])
        >>> def Orlicz_function(u):
        ...     return np.where(u <= 1, u, dc.Decimal(np.inf))
        ...
        >>> dc.getcontext().prec = 20
        >>> p_Amemiya_norm_with_stars_by_decimal(Orlicz_function, x=x, p_norm=dc.Decimal(np.inf),
        ...                                 k_min = dc.Decimal(4)/10,
        ...                                 k_max = dc.Decimal(11)/10,
        ...                                 dk = dc.Decimal(1)/100)
        ...
        (Decimal('1.9999999999999999999'), Decimal('0.50'), Decimal('1.00'))
    """
    if any(x[1, :] <= 0):
        raise ValueError("wrong definition of x(t): x[1, :] must be positive")
    x = abs(x)
    if dk is None:  # if user specifies len_domain_k
        dk = (k_max - k_min) / len_domain_k
    else:
        len_domain_k = (k_max - k_min) * dk
    kappa_domain = []
    # n = dc.Decimal(0)
    # while k_min + n * dk < k_max:
    # # for n in range(len_domain_k):
    #     kappa_domain.append(k_min + n * dk)
    #     n += dc.Decimal(1)
    # kappa_domain = np.array(kappa_domain)
    kappa_domain = np.arange(k_min, k_max, dk)
    kappa_values = []
    if p_norm == 1:
        with tqdm(
                total=len(kappa_domain),
                # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
                # desc="counting of  $1/k*s_p(I_phi)(kx)$ in [" + str(k_min) + "," + str(k_max) + "]",
                desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
                disable=not show_progress
        ) as pbar:
            for k in kappa_domain:
                # print(k, type(k), x[0], x[1])
                kappa_values = np.append(
                    kappa_values,
                    dc.Decimal(1) / k * (1 + np.nansum(Orlicz_function((k * x[0, :])) * x[1, :])),
                )
                pbar.update(1)
    elif p_norm == np.inf:
        with tqdm(
                total=len(kappa_domain),
                # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
                desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
                disable=not show_progress
        ) as pbar:
            for k in kappa_domain:
                kappa_values = np.append(
                    kappa_values,
                    dc.Decimal(1)
                    / k
                    * (
                        max(
                            1,
                            np.nansum(Orlicz_function((k * x[0, :])) * x[1, :]),
                        )
                    ),
                )
                pbar.update(1)
    else:
        with tqdm(
                total=len(kappa_domain),
                # desc="counting of  infimum in [" + str(k_min) + "," + str(k_max) + "]",
                desc=f"counting of  $\\kappa_{{p={p_norm},x}}(k)$ in [" + str(k_min) + "," + str(k_max) + "]",
                disable=not show_progress
        ) as pbar:
            for k in kappa_domain:
                kappa_values = np.append(
                    kappa_values,
                    dc.Decimal(1)
                    / k
                    * (
                            1
                            + (
                                    np.nansum(Orlicz_function((k * x[0, :])) * x[1, :])
                                    ** p_norm
                            )
                    )
                    ** (dc.Decimal(1) / p_norm),
                )
                pbar.update(1)
    # print(array_k)
    kappa_values = np.array(kappa_values)
    accuracy = dc.Decimal(10 ** (-dc.getcontext().prec + 2))  # + 1 is not enough
    osiagane_minimum = np.where(
        np.logical_and(
            kappa_values < kappa_values[np.nanargmin(kappa_values)] + accuracy,
            kappa_values > kappa_values[np.nanargmin(kappa_values)] - accuracy,
        )
    )
    k_star = kappa_domain[np.nanmin(osiagane_minimum)]
    k_star_star = kappa_domain[np.nanmax(osiagane_minimum)]

    if np.nanmin(osiagane_minimum) == 0:
        print('k_star is equal to k_min: try smaller k_min')
    if np.nanmax(osiagane_minimum) == len(kappa_domain) - 1:
        print('k_star_star is equal to k_max: try larger k_max')
    return np.nanmin(kappa_values), k_star, k_star_star  # , kappa_domain, kappa_values


if __name__ == "__main__":
    import doctest  # import the doctest library

    doctest.testmod(verbose=True)  # run the tests and display all results (pass or fail)
