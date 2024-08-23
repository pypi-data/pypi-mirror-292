import numpy as np
from tqdm import tqdm  # for progress bar

def right_side_derivative(Orlicz_function, u_max: float, du: float, show_progress: bool = False):
    """
    Calculates the right-side derivative of the Orlicz function for a given set of parameters.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    u_max : float
        The upper bound of the u domain.
    du : float
        The step size for the u domain.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.

    Returns
    -------
    np.ndarray
        The right-side derivative of the Orlicz function evaluated at each point in the domain of Orlicz_function.

    Examples
    --------
    >>> def Orlicz_function(u):
    ...     return np.where(u <= 1, 0, u ** 2 - 1)
    ...
    >>> right_side_derivative(Orlicz_function, u_max=5, du=0.5)
    array([0. , 0. , 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5])
    """
    u = np.arange(0, u_max, du, dtype=np.float64)  # domain of u
    p_plus = np.zeros(len(u), dtype=np.float64)
    u = np.arange(0, u_max + du, du, dtype=np.float64)
    Phi = Orlicz_function(u)  # potrzebne do wyszukiwania b_Phi
    b_Phi = 0
    for b_Phi in range(len(Phi)):
        if Phi[b_Phi] == np.inf:
            break
    for i in tqdm(range(min(len(p_plus), b_Phi)), desc="counting of  $p_{+}(u)$", disable=not show_progress):
        p_plus[i] = (Phi[i + 1] - Phi[i]) / du  # bellowed has better (inconsistent with du) accuracy (26.06.2024)
        # p_plus[i] = (Orlicz_function(np.array([(i + du) * du])) - Orlicz_function(np.array([i * du]))) / (
        #         du ** 2)  # for better accuracy
    for i in range(b_Phi, len(p_plus)):
        p_plus[i] = np.inf
    # just for len(p_plus)=len(Phi)=len(Psi):
    # p_plus[len(Phi) - 1] = p_plus[len(Phi) - 2]  # może + p_plus[len(Phi) -3]
    # print(type(p_plus))
    return p_plus


def conjugate_function(Orlicz_function, u_max, du: float, show_progress: bool = False):
    """
    Calculates the conjugate function Psi of the Orlicz function for a given set of parameters.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used.
    u_max : float
        The upper bound of the u domain.
    du : float
        The step size for the u domain.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.

    Returns
    -------
    np.ndarray
        The conjugate function Psi of the Orlicz function evaluated at each point in the domain of Orlicz_function.

    Examples
    --------
    >>> def Orlicz_function(u):
    ...     return np.where(u <=1, 0, u**2)
    ...
    >>> conjugate_function(Orlicz_function, u_max=5, du=0.5)
    array([0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 5. ])
    """
    u = np.arange(0, u_max, du)
    Phi = Orlicz_function(u)
    Psi = np.zeros((len(Phi)), dtype=np.float64)
    Psi[:] = np.inf
    for arg in tqdm(range(len(Phi)), desc="counting of  $\\Psi(u)$ by definition", disable=not show_progress):
        wartosci = u[arg] * u - Phi
        if np.argmax(wartosci) == len(wartosci) - 1:  # if maximum is in last argument
            Psi[arg] = np.inf
            break
        else:
            Psi[arg] = np.max(wartosci)
    # print(u_max,len(Phi),Phi,'\n\n',len(Psi), Psi)
    b_Psi = 0
    for b_Psi in range(len(u)):
        if Psi[b_Psi] == np.inf:
            break
    if (
            b_Psi < len(u) - 1
    ):  # może dołożyć Psi(u) = np.nan dla fałszywych b_Psi? i obciąć dziedzinę Psi?
        print("b_Psi =", b_Psi * du, "?")
        new_b_Psi = b_Psi + 1
        n = 0
        try:
            while new_b_Psi > b_Psi and b_Psi < len(u) - 1 and n <= 99:
                print(
                    "trying to extend domain of Phi to check b_Psi - it may take a lot of time -"
                    " press CTRL+C to exit (may not work) or interrupt cell"
                )
                n += 1
                # u_max = 2 * u_max  # nie wiem czy potrzebne (dla podwajania dziedziny) 16.06.2024
                # print(f'teraz u_max = {u_max}')
                if n > 1:  # w pierwszym wejściu jeszcze nie ma nowego Psi
                    old_Phi = new_Phi
                    old_Psi = new_Psi
                    old_len_u = len(new_u)
                if n < 4:
                    print(f'{n}-rd  extending of the Phi domain to check b_Psi')
                else:
                    print(f'\x1b[41m{n}-th extending of the Phi domain to check b_Psi\x1b[0m')
                u_max = (0.1 + 10 ** (1 / n)) * u_max  # ugly function - find another one
                print("u_max = ", u_max)
                new_u = np.arange(0, u_max, du)
                new_Psi = np.zeros((len(new_u)), dtype=np.float64)
                new_Psi[:] = np.inf
                # new_Phi = np.zeros((len(new_u)), dtype=np.float64)
                if n > 1:
                    new_Psi[:b_Psi] = old_Psi[:b_Psi]
                    print('Counting Phi for extended domain')
                    new_Phi = np.append(old_Phi, Orlicz_function(new_u[len(old_Phi):]))
                else:
                    new_Psi[:b_Psi] = Psi[:b_Psi]
                    print('Counting Phi for extended domain')
                    new_Phi = np.append(Phi, Orlicz_function(new_u[len(Phi):]))
                for arg in tqdm(
                        # poniżej len(u) czy len(new_Phi)
                        range(b_Psi, len(u)), desc="counting of  $new_\\Psi(u)$", disable=not show_progress
                        # dlaczego nie len(new_Phi)? Bo nie interesują nas wyjścia poza pierwotną dziedzinę?
                ):
                    new_wartosci = new_u[arg] * new_u - new_Phi
                    if np.argmax(new_wartosci) == len(new_wartosci) - 1:
                        new_Psi[arg] = np.inf
                        break
                    else:
                        new_Psi[arg] = np.max(new_wartosci)
                # print(u_max,len(new_Phi),new_Phi,'\n\n',len(new_Psi), new_Psi)
                for new_b_Psi in range(len(new_u)):
                    if new_Psi[new_b_Psi] == np.inf:
                        break
                if new_b_Psi <= b_Psi:
                    print("YES: b_Psi =", b_Psi * du)
                else:
                    print(
                        "new_b_Psi > b_Psi - problem with domain and/or slowly increasing of Phi"
                    )
                if new_b_Psi > b_Psi:
                    # print(new_b_Psi)
                    print("old_b_Psi", b_Psi * du, "new_b_Psi", new_b_Psi * du)
                    b_Psi = new_b_Psi
                    new_b_Psi += 1
                if n >= 100:
                    print("\x1b[41m Bardzo wątpię w to b_Psi\x1b[0m")
        except KeyboardInterrupt:
            print(
                "b_Psi is very questionable - try changing du or u_max or wait longer next time"
            )
            pass
    # Psi = new_Psi
    # if b_Psi < len(u) - 1:  # for what?
    #     Psi[b_Psi] = np.nan
    # print(Psi,'\n\n', new_Psi)
    try:
        return new_Psi[0:len(Phi)]
    except Exception:
        return Psi

if __name__ == "__main__":
    import doctest  # import the doctest library
    doctest.testmod(verbose=True)  # run the tests and display all results (pass or fail)