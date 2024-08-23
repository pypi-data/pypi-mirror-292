import numpy as np

def Orlicz_function_u_2(u):
    """
    Phi(u) = u^2
    """
    return u ** 2


def Orlicz_function_u_2_u_3(u):
    """
    Phi(u) = u^2 if u<=1 else u^3
    """
    return np.where(u <= 1, u ** 2, u ** 3)


def Orlicz_function_L_1_sum_L_inf(u):
    """
    Phi(u) = 0 if u<=1 else u-1
    """
    return np.where(u <= 1, 0, u - 1)


def Orlicz_function_L_1_cap_L_inf(u):
    """
    Phi(u) = u if u<=1 else np.inf
    """
    return np.where(u <= 1, u, np.inf)


def Orlicz_function_L_1(u):
    """
    Phi(u) = u
    """
    return u


def Orlicz_function_L_inf(u):
    """
    Phi(u) = 0 if u<=1 else np.inf
    """
    return np.where(u <= 1, 0, np.inf)


if __name__ == "__main__":
    import doctest  # import the doctest library

    doctest.testmod(verbose=True)  # run the tests and display all results (pass or fail)
