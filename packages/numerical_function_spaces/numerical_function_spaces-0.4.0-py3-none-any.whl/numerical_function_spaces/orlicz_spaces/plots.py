import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    from norms import *
else:
    from .norms import *
if __name__ == '__main__':
    from conjugate import *
else:
    from .conjugate import *

# my_path = os.path.dirname(
#     os.path.abspath(__file__)
# )  # for save plots
# powyższe podaje ścieżkę do modułu czy do uruchomionego pliku?
# mpl.style.use("default")  # for work with plots on linux via ssh
# print('bieżący katalog: ', my_path)
# mpl.style.use("grayscale")  # do czarno białych wykresów
mpl.rcParams["axes.grid"] = True
mpl.rcParams["grid.linestyle"] = ":"
mpl.rcParams["text.usetex"] = True  # for latex on plots


def plot_save(name: str = 'plot', p_norm: float = ''):
    """
    Saves the current figure in different formats (PNG, SVG, PDF) with a given name and p_norm.

    Parameters
    ----------
    name : str
        The name to be used for the saved files. Default is 'plot'.
    p_norm : float
        The p-norm value to be included in the file names. Default is an empty string.

    Returns
    -------
    The function saves the figure in folder 'plots' : None
    """
    my_path = os.getcwd()
    if not os.path.exists(my_path + '/plots'):
        os.makedirs(my_path + '/plots')
        print(" ! New folder \"plots\" - for plots ")
    else:
        print("Images will be in folder \"plots\" ")
    if not os.path.exists(my_path + '/plots/pdf'):
        os.makedirs(my_path + '/plots/pdf')
        print(" ! New folder \"plots\\pdf\" - for plots in pdf format")
    if not os.path.exists(my_path + '/plots/svg'):
        os.makedirs(my_path + '/plots/svg')
        print(" ! New folder \"plots\\svg\" - for plots in svg format")
    if not os.path.exists(my_path + '/plots/png'):
        os.makedirs(my_path + '/plots/png')
        print(" ! New folder \"plots\\png\" - for plots in png format ")

    plt.savefig(my_path + f"/plots/png/{name}{'_' if p_norm != '' else ''}{p_norm}.png", dpi=1200)
    plt.savefig(my_path + f"/plots/svg/{name}{'_' if p_norm != '' else ''}{p_norm}.svg")
    plt.savefig(my_path + f"/plots/pdf/{name}{'_' if p_norm != '' else ''}{p_norm}.pdf")


def description_for_plot(p_norm: float):
    """
    Set description for plots

    Parameters
    ----------
    p_norm : float
        The p-norm value to be included in plot description
    """
    if p_norm == 1:
        opis = (
            "$\\frac{1}{k}\\left(1+I_{\\Phi}(k\\, x) \\right)$"
        )
    elif p_norm == np.inf:
        opis = (
            "$\\frac{1}{k} \\max \\left(1,I_{\\Phi}(k\\, x)\\right)$"
        )
    else:
        opis = (
            "$\\frac{1}{k}\\left(1+I_{\\Phi}^p(k\\, x) \\right)^{1 / p}$"
        )
    return opis


def plot_p_norms(Orlicz_function,
                 x,
                 # dt,
                 p_min=1,
                 p_max=50,
                 dp=2,
                 attach_inf=False,
                 show_progress=False,
                 figsize: tuple = (5, 4),
                 show: bool = True,
                 save: bool = False,
                 ):
    norms = []
    for ind in tqdm(np.arange(p_min, p_max, dp), disable=not show_progress):
        # norms.append(p_Amemiya_norm_with_stars(Orlicz_function, x, dt, p_norm=ind)[0])
        norms.append(p_Amemiya_norm(Orlicz_function, x, p_norm=ind))
    if attach_inf:
        # norms.append(p_Amemiya_norm_with_stars(Orlicz_function, x, dt, p_norm=np.inf)[0])
        norms.append(p_Amemiya_norm(Orlicz_function, x, p_norm=np.inf))
    fig, ax = plt.subplots(figsize=figsize)
    ax.locator_params(nbins=10, axis='x')
    ax.scatter(p_min, norms[0], label='$||x||_{p=' + str(p_min) + '}=$' + str(norms[0]))
    if attach_inf:
        ax.plot(np.arange(p_min, p_max, dp), norms[0:-1], "-", marker='.', label='$||x||_{p}$')
        ax.plot([np.arange(p_min, p_max, dp)[-1], p_max * 1.3], [norms[-2], norms[-1]], ":")
        # ax.set_xticks(ax.get_xticks().astype(int))  # wrong result for fractional p
        # print(ax.get_xticks())
        ax.scatter(p_max * 1.3, norms[-1], marker='s', label='$||x||_{p=\\infty}=$' + str(norms[-1]))
        ax.set_xticks(list(ax.get_xticks()[1:-2]) + list([p_max * 1.3]),
                      list(ax.get_xticks()[1:-2]) + list(['$\\infty$']))
    else:
        ax.plot(np.arange(p_min, p_max, dp), norms[::], "-", marker='.', label='$||x||_{p}$')
        ax.scatter(np.arange(p_min, p_max, dp)[-1], norms[-1],
                   label='$||x||_{p=' + str(np.arange(p_min, p_max, dp)[-1]) + '}=$' + str(norms[-1]))

    ax.legend()
    ax.annotate("$p$", xy=(1.03, -0.08), xycoords="axes fraction")
    if save is True:
        plot_save(name='p_norms')
    if show is True:
        plt.show()
    plt.close()
    # fig.savefig(my_path + "/plots/p_norms.png", dpi=1200)
    # fig.savefig(my_path + "/plots/p_norms.svg")
    # fig.savefig(my_path + "/plots/p_norms.pdf")


def plot_kappa(
        Orlicz_function,
        x: np.ndarray,
        p_norm: float,
        k_min: float = 0.01,
        k_max: float = 10,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False,
        figsize: tuple = (5, 4),
        show: bool = True,
        save: bool = False,
        save_name: str = None,
        title: str = None
):
    """
    Plot kappa() function and (optionally) save the current figure in different formats (PNG, SVG, PDF) in plots folder.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    x : np.ndarray
        A 2D numpy array representing x(t).
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 0.01.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 10.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.
    figsize : tuple, optional
        Size of plots, by default (5,4)
    show : bool, optional
        Whether to show plot, by default True.
    save : bool, optional
        Whether to save plot in pdf, png, svg formats in plots folder, by default False.
    save_name : string, optional
        Name for saved plots, by default 'kappa_{p_norm}.pdf'
    title : string, optional
        Title for plots, by default 'kappa_{p,x}(k)'

    Returns
    -------
    The function generates a figure and (optionally) save in folder 'plots' : None
    """

    if dk is None:  # if user does not specify dk
        dk = (k_max - k_min) / len_domain_k
    k_accuracy_on_plot = int(np.floor(np.log10(1/dk))+1)
    # else:
    #     len_domain_k == (k_max - k_min) * dk

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

    p_description = p_norm
    fig, ax = plt.subplots(figsize=figsize)
    opis = description_for_plot(p_description)
    norma_x = np.min(array_k)
    b_array_k = 0
    for b_array_k in range(len(array_k)):
        if array_k[b_array_k] == np.inf:
            break
    if p_description != np.inf:
        ax.scatter([], [], facecolors="none",
                   edgecolors="none",
                   label="$p=" + str(p_description) + "$",
                   )
    else:
        ax.scatter([], [], facecolors="none",
                   edgecolors="none",
                   label="$p=\\infty$"
                   )

    if b_array_k < len(array_k) - 1:
        ax.plot(
            domain_k[:b_array_k],
            array_k[:b_array_k],
            label=opis,
            linewidth=2,
        )
        ax.plot(
            domain_k[b_array_k: len(domain_k)],
            np.full(
                (len(domain_k[b_array_k: len(domain_k)])),
                1.3 * max(array_k[:b_array_k]),
            ),
            "--",
            label=opis + "$ = \\infty$",
            linewidth=2,
        )
    else:
        ax.plot(domain_k, array_k, label=opis, linewidth=2)

    accuracy = max((np.max(array_k[np.isfinite(array_k)])
                    - np.min(array_k[np.isfinite(array_k)])) * 0.000001, 1e-15)
    # accuracy = max((np.max(array_k) - np.min(array_k))*0.000001, 1e-15)
    osiagane_minimum = np.where(
        np.logical_and(
            # array_k < array_k[np.argmin(array_k)] + 0.00001,
            # array_k > array_k[np.argmin(array_k)] - 0.00001,
            array_k < array_k[np.argmin(array_k)] + accuracy,
            array_k > array_k[np.argmin(array_k)] - accuracy,
        )
    )

    # y_min, y_max = ax.get_ylim()
    # osiagane_minimum = np.where(
    #     np.logical_and(
    #         # array_k < array_k[np.argmin(array_k)] + 0.00001,
    #         # array_k > array_k[np.argmin(array_k)] - 0.00001,
    #         array_k < array_k[np.argmin(array_k)] + (y_max - y_min) * 0.00001,
    #         array_k > array_k[np.argmin(array_k)] - (y_max - y_min) * 0.00001,
    #     )
    # )

    if array_k[0] > norma_x + accuracy and array_k[-1] > norma_x + accuracy:
        ax.scatter(
            domain_k[osiagane_minimum],
            array_k[osiagane_minimum],
            label="$\\|x\\|\\approx$" + str(norma_x),
        )
    else:
        ax.scatter(
            domain_k[osiagane_minimum],
            array_k[osiagane_minimum],
            label="$\\|x\\|\\leq$" + str(norma_x),
        )
    if np.min(osiagane_minimum) == 0:
        ax.scatter(
            domain_k[np.min(osiagane_minimum)],
            array_k[np.min(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^*(x)\\leq$" + str(np.round(domain_k[np.min(osiagane_minimum)], k_accuracy_on_plot)),
        )
    elif np.min(osiagane_minimum) == len(domain_k) - 1:
        ax.scatter(
            domain_k[np.min(osiagane_minimum)],
            array_k[np.min(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^*(x)\\geq $" + str(np.round(domain_k[np.min(osiagane_minimum)], k_accuracy_on_plot)),
        )
    else:
        ax.scatter(
            domain_k[np.min(osiagane_minimum)],
            array_k[np.min(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^*(x)\\approx$" + str(np.round(domain_k[np.min(osiagane_minimum)], k_accuracy_on_plot)),
        )

    if np.max(osiagane_minimum) == len(domain_k) - 1:
        ax.scatter(
            domain_k[np.max(osiagane_minimum)],
            array_k[np.max(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^{**}(x)\\geq $" + str(np.round(domain_k[np.max(osiagane_minimum)], k_accuracy_on_plot)),
        )
    elif np.max(osiagane_minimum) == 0:
        ax.scatter(
            domain_k[np.max(osiagane_minimum)],
            array_k[np.max(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^{**}(x)\\leq $" + str(np.round(domain_k[np.max(osiagane_minimum)], k_accuracy_on_plot)),
        )
    else:
        ax.scatter(
            domain_k[np.max(osiagane_minimum)],
            array_k[np.max(osiagane_minimum)],
            facecolors="none",
            edgecolors="none",
            label="$k_{p}^{**}(x)\\approx $ " + str(np.round(domain_k[np.max(osiagane_minimum)], k_accuracy_on_plot)),
        )

    ax.locator_params(axis="x", nbins=10)
    ax.legend()
    # ax.annotate("$k$", xy=(0.98, 0.02), xycoords="axes fraction")
    # ax.annotate("$k$", xy=(1.03, -0.1), xycoords="axes fraction")
    ax.set_xlabel("$k$")
    ax.legend()
    # plt.title('$\\frac{1}{k}s_p\\left(I_{\\Phi}\\left(kx\\right)\\right)$')
    if title == None:
        plt.title('$\\kappa_{p,x}\\left(k\\right)$')
    else:
        plt.title(title)

    # fig.autofmt_xdate(rotation=0) # autorotation of the x-axis
    fig.tight_layout()
    # fig.savefig(my_path + "/plots/k_x.png", dpi=1200)
    if save == True:
        if save_name == None:
            plot_save(name='kappa', p_norm=p_norm)
        else:
            plot_save(save_name)

    if show is True:
        plt.show()
    plt.close()
    # fig.savefig(my_path + f"/plots/kappa_{p_norm}.png", dpi=1200)
    # fig.savefig(my_path + f"/plots/kappa_{p_norm}.svg")
    # fig.savefig(my_path + f"/plots/kappa_{p_norm}.pdf")


def plot_Phi_p_plus_Psi(
        Orlicz_function,
        u_max: float,
        du: float,
        max_u_on_plots: float,
        p_plus: np.ndarray = None,
        Psi: np.ndarray = None,
        figsize: tuple = (9, 3),
        show: bool = True,
        save: bool = False,
):
    """
     Plot Orlicz_function, right side derivative and conjugate function on one plot
     and (optionally) save the current figure in different formats (PNG, SVG, PDF) in plots folder.

     Parameters
     ----------
     Orlicz_function : function
         The Orlicz function to be used in form accepting decimal numbers
     du : float
        Step of u_domain for Orlicz function
     u_max: float
         Right limit of u_domain for Orlicz function
     max_u_on_plots: float
         May be the same or smaller to u_max (bigger u_max may improve Psi accuracy)
     p_plus : np.ndarray, optional (if given must use the same u_max and du as given for plot)
         A 1D numpy array representing right side derivative p_{+}(u)
     Psi : np.ndarray, optional (if given must use the same u_max and du as given for plot)
         A 1D numpy array representing right conjugate function Psi(u)
     figsize : tuple, optional
         Size of plots, by default (5,4)
     show : bool, optional
         Whether to show plot, by default True.
     save : bool, optional
         Whether to save plot in pdf, png, svg formats in plots folder, by default False.

     Returns
     -------
     The function generates a figure and (optionally) save in folder 'plots' : None
     """
    u = np.arange(0, u_max, du, dtype=np.float64)  # domain of u

    Phi = Orlicz_function(u)

    if p_plus is None:
        p_plus = right_side_derivative(Orlicz_function, u_max=u_max, du=du)

    if Psi is None:
        Psi = conjugate_function(Orlicz_function, u_max=u_max, du=du)

    b_Phi = 0
    for b_Phi in range(len(Phi)):
        if Phi[b_Phi] == np.inf:
            break
    b_Psi = 0
    for b_Psi in range(len(u)):
        if Psi[b_Psi] == np.inf:
            break
    if b_Psi < len(u) - 1 and b_Psi * du >= 0.95 * max_u_on_plots:
        print(f'\x1b[41m b_Psi > {max_u_on_plots}\x1b[0m')
        max_u_on_plots = 1.3 * b_Psi * du  # to see b_Psi on plotb

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=figsize)

    if b_Phi < len(u) - 1:
        axes[0].plot(
            u[:b_Phi],
            Phi[:b_Phi],
            label="$\\Phi(u)$",
            linewidth=2,
        )
        axes[0].plot(
            u[b_Phi: int(max_u_on_plots / du)],
            np.full(
                (len(u[b_Phi: int(max_u_on_plots / du)])),
                max(1, 2 * max(Phi[: int(b_Phi - 1)])),
            ),
            "--",
            label="$\\Phi(u) = \\infty$",
            linewidth=2,
        )
        axes[1].plot(
            u[:b_Phi],
            p_plus[:b_Phi],
            label="$p_{+}(u)$",
            linewidth=2,
        )
        axes[1].plot(
            u[b_Phi: int(max_u_on_plots / du)],
            np.full(
                (len(u[b_Phi: int(max_u_on_plots / du)])),
                max(1, 2 * max(p_plus[: int(b_Phi - 1)])),
            ),
            "--",
            label="$p_{+}(u) = \\infty$",
            linewidth=2,
        )
    else:
        axes[0].plot(
            u[: int(max_u_on_plots / du)],
            Phi[: int(max_u_on_plots / du)],
            label="$\\Phi(u)$",
            linewidth=2,
        )
        axes[1].plot(
            u[: int(max_u_on_plots / du)],
            p_plus[: int(max_u_on_plots / du)],
            label="$p_{+}(u)$",
            linewidth=2,
        )
    # to avoid strange plot for Phi(u) = u and similars
    axes[1].axis(
        ymin=-0.05 * axes[1].get_ylim()[1],
        ymax=1.05 * axes[1].get_ylim()[1],
    )

    if b_Psi < len(u) - 1:
        axes[2].plot(
            u[:b_Psi],
            Psi[:b_Psi],
            label="$\\Psi(u)$",
            linewidth=2,
        )
        axes[2].plot(
            u[b_Psi: int(max_u_on_plots / du)],
            np.full(
                (len(u[b_Psi: int(max_u_on_plots / du)])),
                max(1, 2 * max(Psi[: int(b_Psi - 1)])),
            ),
            "--",
            label="$\\Psi(u) = \\infty$",
            linewidth=2,
        )
    else:
        axes[2].plot(
            u[: int(max_u_on_plots / du)],
            Psi[: int(max_u_on_plots / du)],
            label="$\\Psi(u)$",
            linewidth=2,
        )
    # fig.suptitle(r'$\Phi(u), p_+(u), \Psi(u)$')
    for ax in axes:
        ax.locator_params(axis="x", nbins=10)
        ax.legend()
    fig.tight_layout()
    if save == True:
        plot_save(name='Phi_p_plus_Psi')
    if show is True:
        plt.show()
    plt.close()
    # fig.savefig(my_path + "/plots/Phi_Psi_pp.png", dpi=1200)
    # fig.savefig(my_path + "/plots/Phi_Psi_pp.svg")
    # fig.savefig(my_path + "/plots/Phi_Psi_pp.pdf")


def plot_Phi(
        Orlicz_function,
        u_max: float,
        du: float,
        max_u_on_plots: float,
        figsize: tuple = (5, 4),
        show: bool = True,
        save: bool = False,
):
    """
     Plot Orlicz_function, right side derivative and conjugate function on one plot
     and (optionally) save the current figure in different formats (PNG, SVG, PDF) in plots folder.

     Parameters
     ----------
     Orlicz_function : function
         The Orlicz function to be used in form accepting decimal numbers
     du : float
        Step of u_domain for Orlicz function
     u_max: float
         Right limit of u_domain for Orlicz function
     max_u_on_plots: float
         May be the same or smaller to u_max (bigger u_max may improve Psi accuracy)
     figsize : tuple, optional
         Size of plots, by default (5,4)
     show : bool, optional
         Whether to show plot, by default True.
     save : bool, optional
         Whether to save plot in pdf, png, svg formats in plots folder, by default False.

     Returns
     -------
     The function generates a figure and (optionally) save in folder 'plots' : None
     """
    u = np.arange(0, u_max, du, dtype=np.float64)  # domain of u

    Phi = Orlicz_function(u)

    b_Phi = 0
    for b_Phi in range(len(Phi)):
        if Phi[b_Phi] == np.inf:
            break
    fig, axes = plt.subplots(figsize=figsize)

    if b_Phi < len(u) - 1:
        axes.plot(
            u[:b_Phi],
            Phi[:b_Phi],
            label="$\\Phi(u)$",
            linewidth=2,
        )
        axes.plot(
            u[b_Phi: int(max_u_on_plots / du)],
            np.full(
                (len(u[b_Phi: int(max_u_on_plots / du)])),
                max(1, 2 * max(Phi[: int(b_Phi - 1)])),
            ),
            "--",
            # "--",  # why this was double? 2024.08.22
            label="$\\Phi(u) = \\infty$",
            linewidth=2,
        )
    else:
        axes.plot(
            u[: int(max_u_on_plots / du)],
            Phi[: int(max_u_on_plots / du)],
            label="$\\Phi(u)$",
            linewidth=2,
        )
    # fig.suptitle(r'$\Phi(u), p_+(u), \Psi(u)$')
    axes.locator_params(axis="x", nbins=10)
    axes.legend()
    fig.tight_layout()
    if save == True:
        plot_save(name='Phi_p_plus_Psi')
    if show is True:
        plt.show()
    plt.close()


def array_for_alpha(
        Orlicz_function,
        du: float,
        u_max: float,
        x: np.ndarray,
        # dt: float,
        p_norm: float,
        p_plus: np.ndarray = None,
        Psi: np.ndarray = None,
        k_min: float = 0.01,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
):
    """
    Calculate domain and values of alpha() function.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    du : float
        Step of u_domain for Orlicz, p_plus and Psi function
    u_max: float
         Right limit of u_domain for Orlicz function
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated.
    p_plus : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right side derivative p_{+}(u)
    Psi : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right conjugate function Psi(u)
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 0.01.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 10.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.

    Returns
    -------
    Two numpy arrays, first for alpha domain, second for alpha values.
    """
    # u_max = len(Psi) * du
    u = np.arange(0, u_max, du, dtype=np.float64)  # domain of u

    Phi = Orlicz_function(u)

    if p_plus is None:
        p_plus = right_side_derivative(Orlicz_function, u_max=u_max, du=du, show_progress=show_progress)

    if Psi is None:
        Psi = conjugate_function(Orlicz_function, u_max=u_max, du=du, show_progress=show_progress)

    if dk is None:  # if user does not specify dk
        dk = (k_max - k_min) / len_domain_k
    # else:
    #     len_domain_k == (k_max - k_min) * dk

    x = abs(x)

    b_p = 0
    for b_p in range(len(p_plus)):
        if p_plus[b_p] == np.inf:
            break
    if p_norm == 1:
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_alpha = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\alpha_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                suma = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            suma = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                suma = np.inf
                            else:
                                p_k_x = int(np.round(p_plus[k_x] / du, 10))
                                if p_k_x > (len(Psi) - 1):  # out of domain Psi
                                    suma = np.nan
                                    if too_big_k is False:
                                        print(
                                            f"for k>{k}: p(kx) is out of Psi domain - "
                                            + "if needs try bigger u_max or smaller k_max"
                                        )
                                    too_big_k = True
                                else:
                                    suma += Psi[p_k_x] * x[1, ind]
                    array_alpha = np.append(array_alpha, suma - 1)
                else:
                    array_alpha = np.append(array_alpha, np.nan)
                pbar.update(1)
        # print(array_alpha)
        return domain_k, array_alpha
    elif p_norm == np.inf:
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_alpha = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\alpha_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                sum_phi = 0
                sum_psi = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            sum_phi = np.nan
                            sum_psi = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                sum_phi = np.inf
                                sum_psi = np.inf
                            else:
                                sum_phi += Phi[k_x] * x[1, ind]
                                p_k_x = int(np.round(p_plus[k_x] / du, 10))
                                if p_k_x > (len(Psi) - 1):  # out of domain Psi
                                    sum_psi = np.nan
                                    if too_big_k is False:
                                        print(
                                            f"for k>{k}: p(kx) is out of Psi domain - "
                                            + "if needs try bigger u_max or smaller k_max"
                                        )
                                    too_big_k = True
                                else:
                                    sum_psi += Psi[p_k_x] * x[1, ind]  # to trzeba przemyśleć, wcześniej było * dt
                    array_alpha = np.append(array_alpha, -1 if sum_phi <= 1 else sum_psi)
                else:
                    array_alpha = np.append(array_alpha, np.nan)
                pbar.update(1)
        # print(array_alpha)
        return domain_k, array_alpha

    else:
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_alpha = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\alpha_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                sum_phi = 0  # osobno do iloczynu całek !!! a nie całki iloczynu !!!
                sum_psi = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            sum_phi = np.nan
                            sum_psi = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                sum_phi = np.inf
                                sum_psi = np.inf
                            else:
                                p_k_x = int(np.round(p_plus[k_x] / du, 10))
                                if p_k_x > (len(Psi) - 1):  # out of domain Psi
                                    sum_phi = np.nan
                                    sum_psi = np.nan
                                    if too_big_k is False:
                                        print(
                                            f"for k>{k}: p(kx) is out of Psi domain - "
                                            + "if needs try bigger u_max or smaller k_max"
                                        )
                                    too_big_k = True
                                else:
                                    sum_phi += (Phi[k_x] * x[1, ind])
                                    sum_psi += (Psi[p_k_x] * x[1, ind])  # wcześniej było * dt
                    array_alpha = np.append(array_alpha, sum_phi ** (p_norm - 1) * sum_psi - 1)
                else:
                    ''' out of domain : sum = np.nan'''
                    array_alpha = np.append(array_alpha, np.nan)
                pbar.update(1)
        # print(array_alpha)
        return domain_k, array_alpha


def plot_alpha(
        Orlicz_function,
        du: float,
        u_max: float,
        x: np.ndarray,
        # dt: float,
        p_norm: float,
        p_plus: np.ndarray = None,
        Psi: np.ndarray = None,
        k_min: float = 0.01,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show: bool = True,
        save: bool = False,
        show_progress: bool = False,
        save_name: str = None,
        title: str = None,
        figsize: tuple = (5, 4),
):
    """
    Plot kappa() function and (optionally) save the current figure in different formats (PNG, SVG, PDF) in plots folder.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    du : float
        Step of u_domain for Orlicz, p_plus and Psi function
    u_max: float
         Right limit of u_domain for Orlicz function
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated.
    p_plus : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right side derivative p_{+}(u)
    Psi : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
     A 1D numpy array representing right conjugate function Psi(u)
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 0.01.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 10.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.
    figsize : tuple, optional
        Size of plots, by default (5, 4)
    show : bool, optional
        Whether to show plot, by default True.
    save : bool, optional
        Whether to save plot in pdf, png, svg formats in plots folder, by default False.
    save_name : string, optional
        Name for saved plots, by default 'kappa_{p_norm}.pdf'
    title : string, optional
        Title for plots, by default 'kappa_{p,x}(k)'

    Note
    ----
    In this function there are no warnings about exceeding k^{*} and k^{**} ranges

    Returns
    -------
    The function generates a figure and (optionally) save in folder 'plots' : None
    """

    domain_k, array_alpha = array_for_alpha(Orlicz_function, du, u_max, x, p_norm, p_plus, Psi, k_min, k_max, dk,
                                            len_domain_k, show_progress)
    if dk is None:  # if user does not specify dk
        dk = (k_max - k_min) / len_domain_k
    k_accuracy_on_plot = int(np.floor(np.log10(1/dk))+1)
    fig, axes = plt.subplots(1, figsize=figsize)
    if p_norm != np.inf:
        axes.scatter([], [], facecolors="none",
                     edgecolors="none",
                     label="$p=" + str(p_norm) + "$",
                     )
    else:
        axes.scatter([], [], facecolors="none",
                     edgecolors="none",
                     label="$p=\\infty$"
                     )
    b_array_alpha = 0
    for b_array_alpha in range(len(array_alpha)):
        if array_alpha[b_array_alpha] == np.inf:
            break

    if p_norm == 1:
        opis = (
            "$I_{\\Phi}^{p-1}(k\\,x)I_{\\Psi} (p_{+} (k\\, x))-1$"
        )
    elif p_norm == np.inf:
        if mpl.rcParams["text.usetex"] is True:
            opis = (r"$\left\{\begin{array}{ll}-1&,\ I_{\Phi}(k\, x) \leq 1 \\"
                    r" I_{\Psi} (p_{+} (k\, x))&,\ I_{\Phi}(k\, x) > 1\end{array}\right.$"
                    )
        else:
            opis = r"$I_{\Psi} (p_{+} (k\, x))$ if $I_{\Phi}(k\, x)) >1 $  else $-1$"
    else:
        opis = (
                "$I_{\\Phi}^{p-1}(k\\, x)"
                + "(I_{\\Psi}(p_{+}(k\\, x)))$"
        )
    # print(array_alpha)

    if b_array_alpha < len(array_alpha) - 1:
        axes.plot(
            domain_k[:b_array_alpha],
            array_alpha[:b_array_alpha],
            label=opis,
            linewidth=2,
        )
        axes.plot(
            domain_k[b_array_alpha: len(domain_k)],
            np.full(
                (len(domain_k[b_array_alpha: len(domain_k)])),
                max(
                    1.2,
                    1.3 * max(array_alpha[:b_array_alpha]),
                ),
            ),
            "--",
            label=opis + " $ = \\infty$",
            linewidth=2,
        )
    else:
        axes.plot(
            domain_k,
            array_alpha,
            label=opis,
            linewidth=2,
        )
    # zmniejszone do 0.001 bo niepracyzyjne obliczenia. Brak monotonicznosci alphy i bety
    accuracy = max((np.max(array_alpha[np.isfinite(array_alpha)])
                    - np.min(array_alpha[np.isfinite(array_alpha)])) * 0.001, 1e-15)
    # accuracy = max((np.max(array_alpha) - np.min(array_alpha)) * 0.000001, 1e-15)
    osiagane_minimum = np.where(
        np.logical_and(
            array_alpha < 1 + accuracy,
            array_alpha > 1 - accuracy,
            # array_alpha < 1 + 0.00001,
            # array_alpha > 1 - 0.00001,
        )
    )

    try:  # lepiej if len(array_alpha) > 0:
        # k_star = domain_k[np.min(np.where(array_alpha > 1 - 0.00001)) - 1]
        # k_star = domain_k[np.min(np.where(array_alpha > 1 - 0.00001))]
        k_star = domain_k[np.min(np.where(array_alpha > - accuracy))]
    except Exception as error:
        print("An exception occurred:", error)
        axes.scatter(
            domain_k[-1],
            array_alpha[-1],
            s=40,
            label="$k_{\\alpha, p}^{*}(x)> k\_max $",
        )
        # print(f'!!!{accuracy}')
        # print(
        #     f'!!! {np.max(array_alpha[np.isfinite(array_alpha)])}, {np.min(array_alpha[np.isfinite(array_alpha)])}')
    else:
        if (
                # array_alpha[np.min(np.where(array_alpha > 1 - 0.00001)) - 1]
                # array_alpha[np.min(np.where(array_alpha > 1 - 0.00001))]
                array_alpha[np.min(np.where(array_alpha > - accuracy))]
                == np.inf
        ):
            y = (
                max(
                    1.2,
                    1.3 * max(array_alpha[:b_array_alpha]),
                ),
            )
        else:
            y = (
                array_alpha[
                    # np.min(np.where(array_alpha > 1 - 0.00001)) - 1
                    # np.min(np.where(array_alpha > 1 - 0.00001))
                    np.min(np.where(array_alpha > - accuracy))
                ],
            )
        axes.scatter(
            # domain_k[np.min(np.where(array_alpha > 1 - 0.00001)) - 1],
            # domain_k[np.min(np.where(array_alpha > 1 - 0.00001))],
            domain_k[np.min(np.where(array_alpha > - accuracy))],
            y,
            marker="*",
            s=100,
            label="$k_{\\alpha, p}^{*}(x)\\approx$" + str(round(k_star, k_accuracy_on_plot)),
        )
        k_star_star = domain_k[
            # np.max(np.where(array_alpha < 1 + 0.00001)) + 1
            # np.max(np.where(array_alpha < 1 + 0.00001))
            np.max(np.where(array_alpha < accuracy))
        ]
        axes.scatter(
            # domain_k[np.max(np.where(array_alpha < 1 + 0.00001)) + 1],
            # domain_k[np.max(np.where(array_alpha < 1 + 0.00001))],
            domain_k[np.max(np.where(array_alpha < accuracy))],
            # array_alpha[np.max(np.where(array_alpha < 1 + 0.00001)) + 1],
            # array_alpha[np.max(np.where(array_alpha < 1 + 0.00001))],
            array_alpha[np.max(np.where(array_alpha < accuracy))],
            s=40,
            label="$k_{\\alpha, p}^{**}(x)\\approx$" + str(round(k_star_star, k_accuracy_on_plot)),
        )

    axes.axhline(
        y=0,
        linestyle="--",
        linewidth=1.3,
        label="0",
    )

    # axes.annotate("$k$", xy=(0.98, 0.02), xycoords="axes fraction")
    # axes.annotate("$k$", xy=(1.03, -0.05), xycoords="axes fraction")
    axes.set_xlabel("$k$")
    axes.legend()
    if title == None:
        plt.title(r'$\alpha_{p,x}(k)$')
    else:
        plt.title(title)

    # fig.suptitle(f"$p={p_norm}$")
    fig.tight_layout()
    if save is True:
        if save_name is None:
            plot_save(name='alpha', p_norm=p_norm)
        else:
            plot_save(save_name)

    if show is True:
        plt.show()
    plt.close()
    # fig.savefig(my_path + f"/plots/alpha_{p_norm}.png", dpi=1200)
    # fig.savefig(my_path + f"/plots/alpha_{p_norm}.svg")
    # fig.savefig(my_path + f"/plots/alpha_{p_norm}.pdf")

def array_for_tau(
        Orlicz_function,
        du: float,
        u_max: float,
        x: np.ndarray,
        # dt: float,
        p_norm: float,
        p_plus: np.ndarray = None,
        Psi: np.ndarray = None,
        k_min: float = 0.01,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show_progress: bool = False
):
    """
    Calculate domain and values of tau() function.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    du : float
        Step of u_domain for Orlicz, p_plus and Psi function
    u_max: float
         Right limit of u_domain for Orlicz function
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated.
    p_plus : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right side derivative p_{+}(u)
    Psi : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right conjugate function Psi(u)
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 0.01.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 10.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.

    Returns
    -------
    Two numpy arrays, first for tau domain, second for tau values.
    """
    # u_max = len(Psi) * du

    u = np.arange(0, u_max, du, dtype=np.float64)  # domain of u

    Phi = Orlicz_function(u)

    if p_plus is None:
        p_plus = right_side_derivative(Orlicz_function, u_max=u_max, du=du, show_progress=show_progress)

    if Psi is None:
        Psi = conjugate_function(Orlicz_function, u_max=u_max, du=du, show_progress=show_progress)

    if dk is None:  # if user does not specify dk
        dk = (k_max - k_min) / len_domain_k
    # else:
    #     len_domain_k == (k_max - k_min) * dk

    x = abs(x)

    b_p = 0
    for b_p in range(len(p_plus)):
        if p_plus[b_p] == np.inf:
            break
    if p_norm == 1:
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_k_star = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\tau_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                suma = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            suma = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                suma = np.inf
                            else:
                                p_k_x = int(np.round(p_plus[k_x] / du, 10))
                                if p_k_x > (len(Psi) - 1):  # out of domain Psi
                                    suma = np.nan
                                    if too_big_k is False:
                                        print(
                                            f"for k>{k}: p(kx) is out of Psi domain - "
                                            + "if needs try bigger u_max or smaller k_max"
                                        )
                                    too_big_k = True
                                else:
                                    suma += Psi[p_k_x] * x[1, ind]
                    array_k_star = np.append(array_k_star, suma)
                else:
                    array_k_star = np.append(array_k_star, np.nan)
                pbar.update(1)
        # print(array_k_star)
        return domain_k, array_k_star
    elif p_norm == np.inf:
        # print('\x1b[41m  Kiedy to działa a kiedy nie - oto jest pytanie (dla odcinkowych nie) \x1b[0m')
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_k_star = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\tau_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                suma = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            suma = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                suma = np.inf
                            else:
                                suma += Phi[k_x] * x[1, ind]
                    array_k_star = np.append(array_k_star, suma)
                else:
                    array_k_star = np.append(array_k_star, np.nan)
                pbar.update(1)
        # print(array_k_star)
        return domain_k, array_k_star

    else:
        q_norm = p_norm / (p_norm - 1)
        # t = np.arange(0, len(x) * dt, dt, dtype=np.float64)
        domain_k = np.arange(k_min, k_max, dk)
        array_k_star = np.array([])
        too_big_k = False  # for print too big k only once
        # with tqdm(total=len(domain_k), desc="counting of  k* and k**", disable=not show_progress) as pbar:
        with tqdm(total=len(domain_k), desc=f"counting of  $\\tau_{{p={p_norm},x}}(k)$",
                  disable=not show_progress) as pbar:
            for k in domain_k:
                sum_phi = 0  # osobne sumy do iloczynu całek a nie całki z iloczynu
                sum_psi = 0
                if too_big_k is False:
                    # print('k=',k)
                    for ind in range(len(x[1, :])):
                        k_x = np.floor(  # albo round albo sufit
                            k * x[0, ind] / du
                        ).astype(int)
                        if k_x > (len(p_plus) - 1):  # out of domain p
                            sum_phi = np.nan
                            sum_psi = np.nan
                            if too_big_k is False:
                                print(
                                    f"for k>{k}: kx is out of p domain - "
                                    + "if needs try bigger u_max or smaller k_max"
                                )
                            too_big_k = True
                        else:
                            if k_x >= b_p:
                                sum_phi = np.inf
                                sum_psi = np.inf
                            else:
                                p_k_x = int(np.round(p_plus[k_x] / du, 10))
                                if p_k_x > (len(Psi) - 1):  # out of domain Psi
                                    sum_phi = np.nan
                                    sum_psi = np.nan
                                    if too_big_k is False:
                                        print(
                                            f"for k>{k}: p(kx) is out of Psi domain - "
                                            + "if needs try bigger u_max or smaller k_max"
                                        )
                                    too_big_k = True
                                else:
                                    sum_phi += (Phi[k_x] * x[1, ind])
                                    sum_psi += (Psi[p_k_x] * x[1, ind])
                    array_k_star = np.append(array_k_star, sum_phi ** (1 / q_norm) * sum_psi ** (1 / p_norm))
                else:
                    ''' out of domain : sum = np.nan'''
                    array_k_star = np.append(array_k_star, np.nan)
                pbar.update(1)
        # print(array_k_star)
        return domain_k, array_k_star

def plot_tau(
        Orlicz_function,
        du: float,
        u_max: float,
        x: np.ndarray,
        # dt: float,
        p_norm: float,
        p_plus: np.ndarray = None,
        Psi: np.ndarray = None,
        k_min: float = 0.01,
        k_max: float = 100,
        dk: float = None,
        len_domain_k: int = 1000,
        show: bool = True,
        save: bool = False,
        show_progress: bool = False,
        save_name: str = None,
        title: str = None,
        figsize: tuple = (5, 4),
):
    """
    Plot tau() function and (optionally) save the current figure in different formats (PNG, SVG, PDF) in plots folder.

    Parameters
    ----------
    Orlicz_function : function
        The Orlicz function to be used in form accepting decimal numbers
    du : float
        Step of u_domain for Orlicz, p_plus and Psi function
    u_max: float
         Right limit of u_domain for Orlicz function
    x : np.ndarray
        A 2D numpy array representing x(t).
    p_norm : float
        The p-norm to be calculated.
    p_plus : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
         A 1D numpy array representing right side derivative p_{+}(u)
    Psi : np.ndarray, optional (must use the same u_max and du as given for plot), by default is None
     A 1D numpy array representing right conjugate function Psi(u)
    k_min : float, optional
        The minimum value of the k domain in decimal form, by default 0.01.
    k_max : float, optional
        The maximum value of the k domain in decimal form, by default 10.
    dk : float, optional
        Step of k_domain, by default None
        When given, more important than len_domain_k
    len_domain_k : int, optional
        The number of points in the k domain, by default 1000.
    show_progress : bool, optional
        Whether to show a progress bar during computation, by default False.
    figsize : tuple, optional
        Size of plots, by default (5, 4)
    show : bool, optional
        Whether to show plot, by default True.
    save : bool, optional
        Whether to save plot in pdf, png, svg formats in plots folder, by default False.
    save_name : string, optional
        Name for saved plots, by default 'kappa_{p_norm}.pdf'
    title : string, optional
        Title for plots, by default 'kappa_{p,x}(k)'

    Note
    ----
    In this function there are no warnings about exceeding k^{*} and k^{**} ranges

    Returns
    -------
    The function generates a figure and (optionally) save in folder 'plots' : None
    """
    domain_k, array_k_star = array_for_tau(Orlicz_function, du, u_max, x, p_norm, p_plus, Psi, k_min, k_max, dk,
                                            len_domain_k, show_progress)
    if dk is None:  # if user does not specify dk
        dk = (k_max - k_min) / len_domain_k
    k_accuracy_on_plot = int(np.floor(np.log10(1/dk))+1)
    fig, axes = plt.subplots(1, figsize=figsize)
    if p_norm != np.inf:
        axes.scatter([], [], facecolors="none",
                     edgecolors="none",
                     label="$p=" + str(p_norm) + "$",
                     )
    else:
        axes.scatter([], [], facecolors="none",
                     edgecolors="none",
                     label="$p=\\infty$"
                     )
    b_array_k_star = 0
    for b_array_k_star in range(len(array_k_star)):
        if array_k_star[b_array_k_star] == np.inf:
            break

    if p_norm == 1:
        opis = (
            "$I_{\\Psi} (p_{+} (k\\, x))$"
        )
    elif p_norm == np.inf:
        opis = (
            "$I_{\\Phi}(k\\, x) $"
        )
    else:
        opis = (
                "$(I_{\\Phi}^{1 / q}(k\\, x))"
                + "(I_{\\Psi}^{1 / p} (p_{+} (k\\, x)))$"
        )
    # print(array_k_star)

    if b_array_k_star < len(array_k_star) - 1:
        axes.plot(
            domain_k[:b_array_k_star],
            array_k_star[:b_array_k_star],
            label=opis,
            linewidth=2,
        )
        axes.plot(
            domain_k[b_array_k_star: len(domain_k)],
            np.full(
                (len(domain_k[b_array_k_star: len(domain_k)])),
                max(
                    1.2,
                    1.3 * max(array_k_star[:b_array_k_star]),
                ),
            ),
            "--",
            label=opis + " $ = \\infty$",
            linewidth=2,
        )
    else:
        axes.plot(
            domain_k,
            array_k_star,
            label=opis,
            linewidth=2,
        )
    accuracy = max((np.max(array_k_star[np.isfinite(array_k_star)])
                    - np.min(array_k_star[np.isfinite(array_k_star)])) * 0.001, 1e-15)
    # accuracy = max((np.max(array_k_star) - np.min(array_k_star)) * 0.000001, 1e-15)
    osiagane_minimum = np.where(
        np.logical_and(
            array_k_star < 1 + accuracy,
            array_k_star > 1 - accuracy,
            # array_k_star < 1 + 0.00001,
            # array_k_star > 1 - 0.00001,
        )
    )

    try:  # lepiej if len(array_k_star) > 0:
        # k_star = domain_k[np.min(np.where(array_k_star > 1 - 0.00001)) - 1]
        # k_star = domain_k[np.min(np.where(array_k_star > 1 - 0.00001))]
        k_star = domain_k[np.min(np.where(array_k_star > 1 - accuracy))]
    except Exception as error:
        print("An exception occurred:", error)
        axes.scatter(
            domain_k[-1],
            array_k_star[-1],
            s=40,
            label="$k_{\\tau, p}^{*}(x)> k\_max $",
        )
        # print(f'!!!{accuracy}')
        # print(
        #     f'!!! {np.max(array_k_star[np.isfinite(array_k_star)])}, {np.min(array_k_star[np.isfinite(array_k_star)])}')
    else:
        if (
                # array_k_star[np.min(np.where(array_k_star > 1 - 0.00001)) - 1]
                # array_k_star[np.min(np.where(array_k_star > 1 - 0.00001))]
                array_k_star[np.min(np.where(array_k_star > 1 - accuracy))]
                == np.inf
        ):
            y = (
                max(
                    1.2,
                    1.3 * max(array_k_star[:b_array_k_star]),
                ),
            )
        else:
            y = (
                array_k_star[
                    # np.min(np.where(array_k_star > 1 - 0.00001)) - 1
                    # np.min(np.where(array_k_star > 1 - 0.00001))
                    np.min(np.where(array_k_star > 1 - accuracy))
                ],
            )
        axes.scatter(
            # domain_k[np.min(np.where(array_k_star > 1 - 0.00001)) - 1],
            # domain_k[np.min(np.where(array_k_star > 1 - 0.00001))],
            domain_k[np.min(np.where(array_k_star > 1 - accuracy))],
            y,
            marker="*",
            s=100,
            label="$k_{\\tau, p}^{*}(x)\\approx$" + str(round(k_star, k_accuracy_on_plot)),
        )
        k_star_star = domain_k[
            # np.max(np.where(array_k_star < 1 + 0.00001)) + 1
            # np.max(np.where(array_k_star < 1 + 0.00001))
            np.max(np.where(array_k_star < 1 + accuracy))
        ]
        axes.scatter(
            # domain_k[np.max(np.where(array_k_star < 1 + 0.00001)) + 1],
            # domain_k[np.max(np.where(array_k_star < 1 + 0.00001))],
            domain_k[np.max(np.where(array_k_star < 1 + accuracy))],
            # array_k_star[np.max(np.where(array_k_star < 1 + 0.00001)) + 1],
            # array_k_star[np.max(np.where(array_k_star < 1 + 0.00001))],
            array_k_star[np.max(np.where(array_k_star < 1 + accuracy))],
            s=40,
            label="$k_{\\tau, p}^{**}(x)\\approx$" + str(round(k_star_star, k_accuracy_on_plot)),
        )

    axes.axhline(
        y=1,
        linestyle="--",
        linewidth=1.3,
        label="1",
    )
    # axes.annotate("$k$", xy=(0.98, 0.02), xycoords="axes fraction")
    # axes.annotate("$k$", xy=(1.03, -0.05), xycoords="axes fraction")
    axes.set_xlabel("$k$")
    axes.legend()
    if title is None:
        plt.title('$\\tau_{p,x}(k)$')
    else:
        plt.title(title)
    # fig.suptitle(f"$p={p_norm}$")
    fig.tight_layout()

    if save is True:
        if save_name is None:
            plot_save(name='tau', p_norm=p_norm)
        else:
            plot_save(save_name)

    if show is True:
        plt.show()
    plt.close()
    # fig.savefig(my_path + f"/plots/tau_{p_norm}.png", dpi=1200)
    # fig.savefig(my_path + f"/plots/tau_{p_norm}.svg")
    # fig.savefig(my_path + f"/plots/tau_{p_norm}.pdf")

if __name__ == "__main__":
    import doctest  # import the doctest library

    doctest.testmod(verbose=True)  # run the tests and display all results (pass or fail)
